import httpx
from bs4 import BeautifulSoup
from sqlalchemy.orm import Session
from .. import models, crud
import asyncio
import re
import logging

logger = logging.getLogger("uvicorn")

# Global cache for slugs
_SLUG_CACHE = {}

async def fetch_directory_slugs():
    """Fetch all country slugs from the directory page"""
    url = "https://www.gov.pl/web/dyplomacja/informacje-dla-podrozujacych"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    slugs = {}
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            links = soup.select('.event-list a') or soup.select('ul > li > a')
            for a in links:
                href = a.get('href', '')
                name = a.get_text(strip=True).lower()
                
                if 'informacje-dla-podrozujacych/' in href:
                    slug = href.split('informacje-dla-podrozujacych/')[-1].split('?')[0].strip('/')
                    if slug:
                        slugs[name] = slug
                elif href.startswith('/web/') and not href.startswith('/web/dyplomacja'):
                    parts = href.strip('/').split('/')
                    if len(parts) >= 2:
                        slugs[name] = parts[1]
            
            logger.info(f"Fetched {len(slugs)} slugs from MSZ directory")
            return slugs
        except Exception as e:
            logger.error(f"Error fetching directory: {e}")
            return {}

async def scrape_country(db: Session, iso_code: str, slug_hint: str = None):
    """Scrape MSZ data for specific country"""
    if iso_code == 'PL': # Skip Poland, MSZ doesn't have "travel info" for Poland on gov.pl
        return {"status": "skipped", "reason": "Home country"}

    country = crud.get_country_by_iso2(db, iso_code)
    if not country:
        return {"error": "Country not found in DB"}

    name_pl = country.name_pl.lower() if country.name_pl else country.name.lower()
    
    slug = slug_hint or _SLUG_CACHE.get(name_pl)
    
    if not slug:
        slug_overrides = {
            'US': 'usa',
            'GB': 'wielkabrytania',
            'AE': 'zjednoczoneemiratyarabskie',
            'KR': 'republika-korei',
            'CZ': 'czechy',
            'VA': 'watykan',
            'TH': 'tajlandia',
            'AU': 'australia',
            'JP': 'japonia',
            'FR': 'francja',
            'DE': 'niemcy',
            'ES': 'hiszpania',
            'IT': 'wlochy',
            'TR': 'turcja',
            'GR': 'grecja',
            'EG': 'egipt',
        }
        slug = slug_overrides.get(iso_code.upper())
    
    if not slug:
        # Better slug generation for gov.pl
        slug = name_pl.replace(' ', '-').replace('ą', 'a').replace('ć', 'c').replace('ę', 'e').replace('ł', 'l').replace('ń', 'n').replace('ó', 'o').replace('ś', 's').replace('ź', 'z').replace('ż', 'z')
        slug = re.sub(r'[^a-z0-9\-]', '', slug)
        slug = slug.replace('-', '') # gov.pl often omits hyphens in country sites

    urls_to_try = [
        f"https://www.gov.pl/web/{slug}/idp",
        f"https://www.gov.pl/web/{slug}/informacje-dla-podrozujacych",
        f"https://www.gov.pl/web/dyplomacja/informacje-dla-podrozujacych/{slug}",
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
                if response.status_code == 200:
                    if str(response.url).strip('/') == "https://www.gov.pl":
                        continue
                    if "bezpieczeństwo" in response.text.lower():
                        response_text = response.text
                        final_url = str(response.url)
                        break
            except:
                continue

    if not response_text:
        return {"error": f"Failed to find valid MSZ page for {iso_code} (slug: {slug})"}

    soup = BeautifulSoup(response_text, 'html.parser')

    # Risk level extraction
    risk_level = "low"
    risk_container = (
        soup.select_one('.travel-advisory--risk-level') or 
        soup.select_one('.safety-level')
    )
    if not risk_container:
        for i in range(1, 5):
            risk_container = soup.select_one(f'.safety-level--{i}')
            if risk_container: break

    if risk_container:
        text = risk_container.get_text().lower()
        if 'zachowaj zwykłą ostrożność' in text: risk_level = 'low'
        elif 'zachowaj szczególną ostrożność' in text: risk_level = 'medium'
        elif 'odradzamy podróże, które nie są konieczne' in text: risk_level = 'high'
        elif 'odradzamy wszelkie podróże' in text: risk_level = 'critical'
    else:
        page_text = soup.get_text().lower()
        if 'odradzamy wszelkie podróże' in page_text: risk_level = 'critical'
        elif 'odradzamy podróże, które nie są konieczne' in page_text: risk_level = 'high'
        elif 'zachowaj szczególną ostrożność' in page_text: risk_level = 'medium'

    # Summary extraction
    summary = ""
    safety_header = None
    for tag in ['h2', 'h3', 'h4']:
        safety_header = soup.find(tag, string=lambda x: x and 'bezpieczeństwo' in x.lower())
        if safety_header: break
            
    if safety_header:
        paragraphs = []
        # Siblings crawl - reliable for gov.pl layout
        curr = safety_header.find_next_sibling()
        count = 0
        while curr and count < 15:
            # Handle nested divs or direct paragraphs
            if curr.name == 'p':
                txt = curr.get_text(strip=True)
                if txt and "Odyseusz" not in txt and "placówką zagraniczną RP" not in txt:
                    paragraphs.append(txt)
                count += 1
            elif curr.name == 'div':
                # Sometimes gov.pl wraps paragraphs in divs
                for p in curr.find_all('p'):
                    txt = p.get_text(strip=True)
                    if txt and "Odyseusz" not in txt:
                        paragraphs.append(txt)
                        count += 1
            elif curr.name in ['h2', 'h3', 'h4']:
                break
            curr = curr.find_next_sibling()
        
        summary = "\n\n".join(paragraphs[:6])

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

async def scrape_all_with_cache(db: Session):
    """Orchestrate scraping all countries using a shared slug cache"""
    global _SLUG_CACHE
    _SLUG_CACHE = await fetch_directory_slugs()
    
    countries = db.query(models.Country).all()
    results = {"success": 0, "errors": 0, "details": []}

    for i, country in enumerate(countries):
        try:
            logger.info(f"[{i+1}/{len(countries)}] Scraping {country.name_pl or country.name} ({country.iso_alpha2})...")
            res = await scrape_country(db, country.iso_alpha2)
            if "error" in res:
                results["errors"] += 1
                logger.error(f"  - Error: {res['error']}")
            else:
                results["success"] += 1
                logger.info(f"  - Success: {res['risk_level']} ({res.get('url', 'N/A')})")
            await asyncio.sleep(0.5) 
        except Exception as e:
            results["errors"] += 1
            results["details"].append(f"{country.iso_alpha2}: {str(e)}")
            logger.error(f"  - Exception: {str(e)}")

    return results
