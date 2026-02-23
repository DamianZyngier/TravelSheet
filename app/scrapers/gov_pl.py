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

def clean_name(name):
    """Clean name for better matching with MSZ directory"""
    if not name: return ""
    name = re.sub(r'\(.*?\)', '', name)
    name = name.split(',')[0]
    return name.strip().lower()

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
            
            # Find all /web/dyplomacja/SLUG links followed by a title div
            matches = re.findall(r'<a href="/web/dyplomacja/([^"]+)">\s*<div>\s*<div class="title">([^<]+)', response.text)
            
            for slug, name in matches:
                name_clean = clean_name(name)
                slug_clean = slug.strip().split('?')[0].strip('/')
                if slug_clean and name_clean:
                    slugs[name_clean] = slug_clean
            
            logger.info(f"Fetched {len(slugs)} slugs from MSZ directory")
            return slugs
        except Exception as e:
            logger.error(f"Error fetching directory: {e}")
            return {}

async def scrape_country(db: Session, iso_code: str):
    """Scrape MSZ data for specific country"""
    if iso_code == 'PL':
        return {"status": "skipped", "reason": "Home country"}

    country = db.query(models.Country).filter(models.Country.iso_alpha2 == iso_code).first()
    if not country:
        return {"error": "Country not found in DB"}

    name_pl = clean_name(country.name_pl or country.name)
    
    # TERRITORY MAPPING: Map dependencies to parent countries
    TERRITORY_MAPPING = {
        'AW': 'holandia', 'BQ': 'holandia', 'CW': 'holandia', 'SX': 'holandia',
        'GF': 'francja', 'GP': 'francja', 'MQ': 'francja', 'RE': 'francja', 'YT': 'francja',
        'BL': 'francja', 'MF': 'francja', 'PM': 'francja', 'WF': 'francja', 'PF': 'francja', 'NC': 'francja', 'TF': 'francja',
        'BM': 'wielkabrytania', 'VG': 'wielkabrytania', 'KY': 'wielkabrytania', 'MS': 'wielkabrytania', 
        'TC': 'wielkabrytania', 'FK': 'wielkabrytania', 'GI': 'wielkabrytania', 'SH': 'wielkabrytania', 
        'IO': 'wielkabrytania', 'PN': 'wielkabrytania', 'GS': 'wielkabrytania', 'AI': 'wielkabrytania',
        'JE': 'wielkabrytania', 'GG': 'wielkabrytania', 'IM': 'wielkabrytania',
        'AS': 'usa', 'GU': 'usa', 'MP': 'usa', 'PR': 'usa', 'VI': 'usa', 'UM': 'usa',
        'CX': 'australia', 'CC': 'australia', 'NF': 'australia', 'HM': 'australia',
        'CK': 'nowa-zelandia', 'NU': 'nowa-zelandia', 'TK': 'nowa-zelandia',
        'GL': 'dania', 'FO': 'dania', 'SJ': 'norwegia', 'BV': 'norwegia', 'AX': 'finlandia',
        'MO': 'chiny', 'HK': 'hongkong', 'AQ': 'argentyna', 'EH': 'maroko'
    }
    
    # Try directory cache first, then territory mapping
    slug = _SLUG_CACHE.get(name_pl)
    if not slug:
        slug = TERRITORY_MAPPING.get(iso_code.upper())

    # Predefined manual overrides for discrepancies
    OVERRIDE_MAPPING = {
        'US': 'usa', 'GB': 'wielkabrytania', 'AE': 'zea', 'BN': 'brunei-darussalam',
        'KR': 'republika-korei', 'CZ': 'czechy', 'VA': 'watykan', 'VN': 'wietnam',
        'LA': 'laos', 'MK': 'macedonia', 'CI': 'wybrzeze-kosci-sloniowej',
        'CD': 'demokratyczna-republika-kong', 'CG': 'kongo', 'ZA': 'republika-poludniowej-afryki',
        'KN': 'saint-kitts-i-nevis', 'SZ': 'eswatini', 'ST': 'wyspy-swietego-tomasza-i-ksiazeca',
        'CV': 'republika-zielonego-przyladka', 'TL': 'timor-wschodni'
    }
    
    if not slug or iso_code.upper() in OVERRIDE_MAPPING:
        slug = OVERRIDE_MAPPING.get(iso_code.upper(), slug)

    if not slug:
        # Fallback slug generation
        slug = name_pl.replace(' ', '-').replace('ą', 'a').replace('ć', 'c').replace('ę', 'e').replace('ł', 'l').replace('ń', 'n').replace('ó', 'o').replace('ś', 's').replace('ź', 'z').replace('ż', 'z')
        slug = re.sub(r'[^a-z0-9\-]', '', slug)

    slug_no_hyphen = slug.replace('-', '')
    
    urls_to_try = [
        f"https://www.gov.pl/web/dyplomacja/{slug}",
        f"https://www.gov.pl/web/{slug}/idp",
        f"https://www.gov.pl/web/{slug}/informacje-dla-podrozujacych",
        f"https://www.gov.pl/web/dyplomacja/{slug_no_hyphen}",
        f"https://www.gov.pl/web/{slug_no_hyphen}/idp",
        f"https://www.gov.pl/web/{slug_no_hyphen}/informacje-dla-podrozujacych",
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
                    curr_url = str(response.url).rstrip('/')
                    if curr_url == "https://www.gov.pl" or curr_url == "https://www.gov.pl/web/dyplomacja/informacje-dla-podrozujacych":
                        continue
                    if "bezpieczeństwo" in response.text.lower() or "travel advisory" in response.text.lower():
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
    risk_container = soup.select_one('.travel-advisory--risk-level') or soup.select_one('.safety-level')
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
        curr = safety_header.find_next_sibling()
        count = 0
        while curr and count < 15:
            if curr.name == 'p':
                txt = curr.get_text(strip=True)
                if txt and not any(x in txt for x in ["Odyseusz", "placówką zagraniczną RP"]):
                    paragraphs.append(txt)
                count += 1
            elif curr.name == 'div':
                for p in curr.find_all('p'):
                    txt = p.get_text(strip=True)
                    if txt and "Odyseusz" not in txt:
                        if txt not in paragraphs:
                            paragraphs.append(txt)
                            count += 1
            elif curr.name in ['h2', 'h3', 'h4']:
                break
            curr = curr.find_next_sibling()
        summary = "\n\n".join(paragraphs[:6])

    if not summary:
        desc_meta = soup.find('meta', {'property': 'og:description'})
        if desc_meta:
            summary = desc_meta.get('content', '')

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
    """Batch scrape all countries"""
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
            elif res.get("status") == "skipped":
                results["success"] += 1
                logger.info(f"  - Skipped: {res['reason']}")
            else:
                results["success"] += 1
                logger.info(f"  - Success: {res['risk_level']} ({res.get('url', 'N/A')})")
            await asyncio.sleep(0.5) 
        except Exception as e:
            results["errors"] += 1
            results["details"].append(f"{country.iso_alpha2}: {str(e)}")
            logger.error(f"  - Exception: {str(e)}")

    return results
