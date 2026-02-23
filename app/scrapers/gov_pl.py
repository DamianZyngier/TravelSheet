import httpx
from bs4 import BeautifulSoup
from sqlalchemy.orm import Session
from .. import models, crud
import asyncio
import re

async def get_country_slugs():
    """Fetch all country slugs from the directory page"""
    url = "https://www.gov.pl/web/dyplomacja/informacje-dla-podrozujacych"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find all links in the directory
            slugs = {}
            # Links are usually in an <ul> within the content
            links = soup.select('ul > li > a')
            for a in links:
                href = a.get('href', '')
                name = a.get_text(strip=True).lower()
                
                # Extract slug from href: /web/dyplomacja/informacje-dla-podrozujacych/tajlandia
                # Or sometimes it might be a direct link to a country site
                if 'informacje-dla-podrozujacych/' in href:
                    slug = href.split('informacje-dla-podrozujacych/')[-1].split('?')[0].strip('/')
                    if slug:
                        slugs[name] = slug
            return slugs
        except Exception as e:
            print(f"Error fetching directory: {e}")
            return {}

async def scrape_country(db: Session, iso_code: str):
    """Scrape MSZ data for specific country"""

    country = crud.get_country_by_iso2(db, iso_code)
    if not country:
        return {"error": "Country not found in DB"}

    # Try to find slug by Polish name
    name_pl = country.name_pl.lower() if country.name_pl else country.name.lower()
    
    # Predefined common overrides for discrepancies
    slug_overrides = {
        'US': 'stany-zjednoczone-ameryki',
        'GB': 'wielka-brytania',
        'AE': 'zjednoczone-emiraty-arabskie',
        'KR': 'republika-korei',
        'CZ': 'republika-czeska',
        'VA': 'stolica-apostolska-watykan',
    }
    
    slug = slug_overrides.get(iso_code.upper())
    
    if not slug:
        # Fallback to name-based slug generation
        slug = name_pl.replace(' ', '-').replace('ą', 'a').replace('ć', 'c').replace('ę', 'e').replace('ł', 'l').replace('ń', 'n').replace('ó', 'o').replace('ś', 's').replace('ź', 'z').replace('ż', 'z')
        # Clean up
        slug = re.sub(r'[^a-z0-9\-]', '', slug)

    # User provided a hint: https://www.gov.pl/web/{slug}/idp or /informacje-dla-podrozujacych
    # We will try both
    urls_to_try = [
        f"https://www.gov.pl/web/dyplomacja/informacje-dla-podrozujacych/{slug}",
        f"https://www.gov.pl/web/{slug}/idp",
        f"https://www.gov.pl/web/{slug}/informacje-dla-podrozujacych"
    ]

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    response_text = None
    final_url = None

    async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
        for url in urls_to_try:
            try:
                response = await client.get(url, headers=headers)
                if response.status_code == 200 and "Portal Gov.pl" in response.text and len(response.text) > 5000:
                    # Check if it's not just the homepage (usually homepages have shorter/different titles)
                    # This is a bit tricky with gov.pl as many pages have the same title
                    if "informacje" in response.text.lower() or "bezpieczeństwo" in response.text.lower():
                        response_text = response.text
                        final_url = url
                        break
            except:
                continue

    if not response_text:
        return {"error": f"Failed to find valid MSZ page for {iso_code} (slug: {slug})"}

    soup = BeautifulSoup(response_text, 'html.parser')

    # Extract Risk Level
    risk_level = "unknown"
    risk_container = soup.select_one('.travel-advisory--risk-level') or soup.select_one('.safety-level')
    
    # Fallback to checking specific classes safety-level--X
    if not risk_container:
        for i in range(1, 5):
            risk_container = soup.select_one(f'.safety-level--{i}')
            if risk_container: break

    if risk_container:
        text = risk_container.get_text().lower()
        if 'zachowaj zwykłą ostrożność' in text:
            risk_level = 'low'
        elif 'zachowaj szczególną ostrożność' in text:
            risk_level = 'medium'
        elif 'odradzamy podróże, które nie są konieczne' in text:
            risk_level = 'high'
        elif 'odradzamy wszelkie podróże' in text:
            risk_level = 'critical'
    else:
        # Final fallback keyword search
        page_text = soup.get_text().lower()
        if 'odradzamy wszelkie podróże' in page_text:
            risk_level = 'critical'
        elif 'odradzamy podróże, które nie są konieczne' in page_text:
            risk_level = 'high'
        elif 'zachowaj szczególną ostrożność' in page_text:
            risk_level = 'medium'
        elif 'zachowaj zwykłą ostrożność' in page_text:
            risk_level = 'low'

    # Extract Safety Summary
    summary = ""
    headers_to_check = soup.find_all(['h2', 'h3', 'h4'])
    safety_header = None
    for h in headers_to_check:
        h_text = h.get_text().lower()
        if 'bezpieczeństwo' in h_text:
            safety_header = h
            break
            
    if safety_header:
        paragraphs = []
        curr = safety_header.find_next_sibling()
        count = 0
        while curr and count < 10:
            if curr.name == 'p':
                txt = curr.get_text(strip=True)
                if txt: paragraphs.append(txt)
                count += 1
            elif curr.name in ['h2', 'h3', 'h4']:
                break
            curr = curr.find_next_sibling()
        summary = "\n\n".join(paragraphs)

    # Update or create safety info
    safety = db.query(models.SafetyInfo).filter(models.SafetyInfo.country_id == country.id).first()
    if safety:
        safety.risk_level = risk_level
        safety.summary = summary[:1500]
        safety.full_url = final_url
    else:
        safety = models.SafetyInfo(country_id=country.id, risk_level=risk_level, summary=summary[:1500], full_url=final_url)
        db.add(safety)

    db.commit()
    return {"status": "success", "risk_level": risk_level, "summary_len": len(summary), "url": final_url}
