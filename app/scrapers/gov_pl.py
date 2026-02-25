import httpx
from bs4 import BeautifulSoup
from sqlalchemy.orm import Session
from .. import models, crud
import asyncio
import re
import logging
from .utils import GOV_PL_MANUAL_MAPPING, clean_polish_name, slugify, get_headers

logger = logging.getLogger("uvicorn")

# Global cache for slugs
_SLUG_CACHE = {}

async def fetch_directory_slugs():
    """Fetch all country slugs from the directory page"""
    url = "https://www.gov.pl/web/dyplomacja/informacje-dla-podrozujacych"
    headers = get_headers()
    slugs = {}
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            matches = re.findall(r'<a href="/web/dyplomacja/([^"]+)">\s*<div>\s*<div class="title">([^<]+)', response.text)
            for slug, name in matches:
                name_clean = clean_polish_name(name)
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

    name_pl = clean_polish_name(country.name_pl or country.name)
    slug = _SLUG_CACHE.get(name_pl) or GOV_PL_MANUAL_MAPPING.get(iso_code.upper())
    
    if not slug:
        slug = slugify(name_pl).replace('-', '') # MSZ often uses no hyphens in slugs

    urls_to_try = [
        f"https://www.gov.pl/web/dyplomacja/{slug}",
        f"https://www.gov.pl/web/{slug}/idp",
        f"https://www.gov.pl/web/{slug}/informacje-dla-podrozujacych",
    ]

    headers = get_headers()
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
            except: continue

    if not response_text:
        return {"error": f"Failed to find valid MSZ page for {iso_code} (slug: {slug})"}

    soup = BeautifulSoup(response_text, 'html.parser')
    risk_level = "low"
    
    risk_container = soup.select_one('.travel-advisory--risk-level') or soup.select_one('.safety-level')
    if not risk_container:
        for i in range(1, 5):
            risk_container = soup.select_one(f'.safety-level--{i}')
            if risk_container: break

    if risk_container:
        text_l = risk_container.get_text().strip().lower()
        if 'zachowaj zwykłą ostrożność' in text_l: risk_level = 'low'
        elif 'zachowaj szczególną ostrożność' in text_l: risk_level = 'medium'
        elif 'odradzamy podróże, które nie są konieczne' in text_l: risk_level = 'high'
        elif 'odradzamy wszelkie podróże' in text_l: risk_level = 'critical'
    
    # Fallback/Override by keyword search in whole page
    page_text = soup.get_text().lower()
    if 'odradza wszelkie podróże' in page_text or 'odradzamy wszelkie podróże' in page_text: 
        risk_level = 'critical'
    elif risk_level == 'low': # Only check other keywords if still low
        if 'odradza podróże, które nie są konieczne' in page_text or 'odradzamy podróże, które nie są konieczne' in page_text: 
            risk_level = 'high'
        elif 'zachowanie szczególnej ostrożności' in page_text or 'zachowaj szczególną ostrożność' in page_text: 
            risk_level = 'medium'

    # Phrasing per risk level
    country_name = country.name_pl
    if risk_level == 'critical':
        risk_phrase = f"MSZ odradza wszelkie podróże do tego kraju ({country_name})."
    elif risk_level == 'high':
        risk_phrase = f"MSZ odradza podróże, które nie są konieczne do tego kraju ({country_name})."
    elif risk_level == 'medium':
        risk_phrase = f"MSZ zaleca zachowanie szczególnej ostrożności podczas podróży do tego kraju ({country_name})."
    else:
        risk_phrase = f"MSZ zaleca zachowanie zwykłej ostrożności podczas podróży do tego kraju ({country_name})."

    # Extract additional details
    risk_details_list = []
    advisory_el = soup.select_one('.travel-advisory--description')
    if advisory_el:
        risk_details_list.append(advisory_el.get_text().strip())
        
    alerts = soup.select('.alert-danger, .alert-warning')
    for alert in alerts:
        text = alert.get_text().strip()
        if text and text not in risk_details_list:
            risk_details_list.append(text)
            
    risk_details = "\n\n".join(risk_details_list)
    
    # Update Safety
    safety = db.query(models.SafetyInfo).filter(models.SafetyInfo.country_id == country.id).first()
    if not safety:
        safety = models.SafetyInfo(country_id=country.id)
        db.add(safety)
    safety.risk_level, safety.summary, safety.full_url = risk_level, risk_phrase, final_url
    safety.risk_details = risk_details

    # Docs & Visa
    passport_req, temp_passport_req, id_card_req, visa_req = True, True, False, False
    raw_text = soup.get_text()
    
    docs_section = soup.find(string=re.compile(r'Na jakim dokumencie', re.I))
    if docs_section:
        docs_text = ""
        curr = docs_section.parent
        for _ in range(10):
            if curr:
                docs_text += curr.get_text()
                curr = curr.find_next_sibling()
        
        if re.search(r'Paszport:.*?TAK', docs_text, re.I | re.S): passport_req = True
        elif re.search(r'Paszport:.*?NIE', docs_text, re.I | re.S): passport_req = False
        
        if re.search(r'Paszport tymczasowy:.*?TAK', docs_text, re.I | re.S): temp_passport_req = True
        elif re.search(r'Paszport tymczasowy:.*?NIE', docs_text, re.I | re.S): temp_passport_req = False
        
        if re.search(r'Dowód osobisty:.*?TAK', docs_text, re.I | re.S): id_card_req = True
        elif re.search(r'Dowód osobisty:.*?NIE', docs_text, re.I | re.S): id_card_req = False
    
    visa_section = soup.find(string=re.compile(r'Czy trzeba wyrobić wizę', re.I))
    if visa_section:
        visa_text = ""
        curr = visa_section.parent
        for _ in range(8):
            if curr:
                visa_text += curr.get_text()
                curr = curr.find_next_sibling()
        
        if any(x in visa_text.lower() for x in ["nie muszą mieć wizy", "nie jest wymagana wiza", "ruch bezwizowy", "bezwizowo", "bezwizowy"]):
            visa_req = False
        elif any(x in visa_text.lower() for x in ["wymagana jest wiza", "obowiązek wizowy", "muszą posiadać wizę", "wizę należy uzyskać"]):
            visa_req = True
    else:
        if "nie muszą mieć wizy" in raw_text.lower() or "bezwizowo" in raw_text.lower(): visa_req = False
        elif "wymagana jest wiza" in raw_text.lower(): visa_req = True

    if country.continent == 'Europe' and iso_code not in ['BY', 'RU', 'UA', 'GB']:
        id_card_req, visa_req = True, False

    entry = db.query(models.EntryRequirement).filter(models.EntryRequirement.country_id == country.id).first()
    if not entry:
        entry = models.EntryRequirement(country_id=country.id)
        db.add(entry)
    entry.passport_required = passport_req
    entry.temp_passport_allowed = temp_passport_req
    entry.id_card_allowed = id_card_req
    entry.visa_required = visa_req

    # Health & Vaccinations
    vaccines_req, vaccines_sug, health_full = "", "", ""
    health_section = soup.find(string=re.compile(r'^Zdrowie$', re.I)) or soup.find(string=re.compile(r'Informacje dotyczące zdrowia', re.I))
    if health_section:
        health_text_list = []
        curr = health_section.parent
        for _ in range(25):
            if curr:
                txt = curr.get_text().strip()
                if txt: health_text_list.append(txt)
                curr = curr.find_next_sibling()
                if curr and curr.name in ['h2', 'h3']: break
        
        health_full = "\n\n".join(health_text_list)
        health_text_lower = health_full.lower()
        
        if "żółtą febrę" in health_text_lower or "żółtej febry" in health_text_lower:
            if "obowiązkowe" in health_text_lower or "wymagane" in health_text_lower:
                vaccines_req = "Szczepienie przeciw żółtej febrze (wymagane)"
        
        suggested_list = []
        for v in ["tężec", "błonica", "krztusiec", "dur brzuszny", "WZW A", "WZW B", "wścieklizna", "cholera", "polio"]:
            if v.lower() in health_text_lower:
                suggested_list.append(v)
        
        if suggested_list:
            vaccines_sug = "Zalecane: " + ", ".join(suggested_list)

    practical = db.query(models.PracticalInfo).filter(models.PracticalInfo.country_id == country.id).first()
    if not practical:
        practical = models.PracticalInfo(country_id=country.id)
        db.add(practical)
    practical.vaccinations_required = vaccines_req
    practical.vaccinations_suggested = vaccines_sug
    practical.health_info = health_full

    db.commit()
    return {"status": "success", "risk_level": risk_level, "url": final_url}

async def scrape_all_with_cache(db: Session):
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
                results["details"].append(f"{country.iso_alpha2}: {res['error']}")
            else: results["success"] += 1
            await asyncio.sleep(0.5) 
        except Exception as e:
            results["errors"] += 1
            results["details"].append(f"{country.iso_alpha2}: {str(e)}")
    return results
