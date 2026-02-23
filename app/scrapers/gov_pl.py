import httpx
from bs4 import BeautifulSoup
from sqlalchemy.orm import Session
from .. import models, crud
import asyncio

# Mapowanie ISO -> slug gov.pl
COUNTRY_SLUGS = {
    'TH': 'tajlandia',
    'PL': 'polska',
    'DE': 'niemcy',
    'FR': 'francja',
    'EG': 'egipt',
    'IT': 'wlochy',
    'GR': 'grecja',
    'ES': 'hiszpania',
    'TR': 'turcja',
    'HR': 'chorwacja',
    'US': 'stany-zjednoczone-ameryki',
    'GB': 'wielka-brytania',
    'JP': 'japonia',
    'AE': 'zjednoczone-emiraty-arabskie',
    'CY': 'cypr',
    'PT': 'portugalia',
    'MA': 'maroko',
    'TN': 'tunezja',
    'BR': 'brazylia',
    'CZ': 'republika-czeska',
    'AT': 'austria',
}

async def scrape_country(db: Session, iso_code: str):
    """Scrape MSZ data for specific country"""

    slug = COUNTRY_SLUGS.get(iso_code.upper())
    if not slug:
        return {"error": f"No slug mapping for {iso_code}"}

    url = f"https://www.gov.pl/web/dyplomacja/informacje-dla-podrozujacych/{slug}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
        try:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
        except Exception as e:
            return {"error": f"Failed to fetch {url}: {str(e)}"}

    soup = BeautifulSoup(response.text, 'html.parser')

    country = crud.get_country_by_iso2(db, iso_code)
    if not country:
        return {"error": "Country not found in DB"}

    # Extract Risk Level from MSZ specific classes
    risk_level = "unknown"
    
    # Try multiple selectors for safety levels
    risk_container = (
        soup.select_one('.travel-advisory--risk-level') or 
        soup.select_one('.safety-level') or
        soup.select_one('.safety-level--1') or
        soup.select_one('.safety-level--2') or
        soup.select_one('.safety-level--3') or
        soup.select_one('.safety-level--4')
    )
    
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
        # Fallback: check all text for keywords
        page_text = soup.get_text().lower()
        if 'odradzamy wszelkie podróże' in page_text:
            risk_level = 'critical'
        elif 'odradzamy podróże, które nie są konieczne' in page_text:
            risk_level = 'high'
        elif 'zachowaj szczególną ostrożność' in page_text:
            risk_level = 'medium'
        elif 'zachowaj zwykłą ostrożność' in page_text:
            risk_level = 'low'

    # Extract Safety Summary - search for the section after h3 "Bezpieczeństwo"
    summary = ""
    # Look for headers containing "Bezpieczeństwo"
    headers_to_check = soup.find_all(['h2', 'h3', 'h4'])
    safety_header = None
    for h in headers_to_check:
        if 'bezpieczeństwo' in h.get_text().lower():
            safety_header = h
            break
            
    if safety_header:
        # Get next few paragraphs or the whole div content
        paragraphs = []
        curr = safety_header.find_next_sibling()
        count = 0
        while curr and count < 10: # Look at up to 10 next elements
            if curr.name == 'p':
                txt = curr.get_text(strip=True)
                if txt:
                    paragraphs.append(txt)
                count += 1
            elif curr.name in ['h2', 'h3', 'h4']: # Stop at next section
                break
            curr = curr.find_next_sibling()
        summary = "\n\n".join(paragraphs)

    # Update or create safety info
    safety = db.query(models.SafetyInfo).filter(models.SafetyInfo.country_id == country.id).first()
    if safety:
        safety.risk_level = risk_level
        safety.summary = summary[:1000]
        safety.full_url = url
    else:
        safety = models.SafetyInfo(country_id=country.id, risk_level=risk_level, summary=summary[:1000], full_url=url)
        db.add(safety)

    db.commit()
    return {"status": "success", "risk_level": risk_level, "summary_len": len(summary)}

    return {
        "country": iso_code,
        "slug": slug,
        "scraped": True
    }
