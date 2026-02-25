import httpx
from bs4 import BeautifulSoup
from sqlalchemy.orm import Session
from .. import models, crud
import asyncio
import re
import logging
from sqlalchemy import func
from .utils import MSZ_GOV_PL_MANUAL_MAPPING, clean_polish_name, slugify, get_headers

logger = logging.getLogger("uvicorn")

# Global cache for slugs
_SLUG_CACHE = {}

async def fetch_directory_slugs():
    """Fetch all country slugs from the directory page"""
    url = "https://www.gov.pl/web/dyplomacja/informacje-dla-podrozujacych"
    headers = get_headers()
    slugs = {}
    async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
        try:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            # The directory uses <li> elements with <a> inside
            links = soup.select('div.article-content ul li a')
            if not links:
                # Fallback to a broader selector if structure changed
                links = soup.select('a[href*="/web/dyplomacja/"]')
            
            for a in links:
                href = a.get('href', '')
                title_div = a.select_one('.title') or a
                if href:
                    name = title_div.get_text().strip()
                    # Extract slug from /web/dyplomacja/slug
                    slug_match = re.search(r'/web/dyplomacja/([^/?#\s]+)', href)
                    if slug_match:
                        slug = slug_match.group(1)
                        if slug != "informacje-dla-podrozujacych":
                            name_clean = clean_polish_name(name)
                            slugs[name_clean] = slug
            
            _SLUG_CACHE.update(slugs)
            logger.info(f"Fetched {len(slugs)} slugs from MSZ directory")
            return slugs
        except Exception as e:
            logger.error(f"Error fetching directory: {e}")
            return {}

async def scrape_country(db: Session, iso_code: str):
    """Scrape MSZ data for specific country"""
    if iso_code.upper() == 'PL':
        return {"status": "skipped", "reason": "Home country"}

    country = db.query(models.Country).filter(models.Country.iso_alpha2 == iso_code.upper()).first()
    if not country:
        return {"error": "Country not found in DB"}

    name_pl = clean_polish_name(country.name_pl or country.name)
    
    # 1. Try from cache (directory page)
    slug = _SLUG_CACHE.get(name_pl)
    
    # 2. Try from manual mapping
    if not slug:
        slug = MSZ_GOV_PL_MANUAL_MAPPING.get(iso_code.upper())
    
    urls_to_try = []
    if slug:
        # If we have a slug, these are the most likely patterns
        urls_to_try = [
            f"https://www.gov.pl/web/dyplomacja/{slug}",
            f"https://www.gov.pl/web/{slug}/informacje-dla-podrozujacych",
            f"https://www.gov.pl/web/{slug}/idp",
        ]
    else:
        # Guessed slug as fallback
        guessed_slug = slugify(name_pl).replace('-', '')
        urls_to_try = [f"https://www.gov.pl/web/dyplomacja/{guessed_slug}"]

    headers = get_headers()
    response_text = None
    final_url = None
    last_status = None

    async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
        for i, url in enumerate(urls_to_try):
            try:
                response = await client.get(url, headers=headers)
                last_status = response.status_code
                if response.status_code == 200:
                    curr_url = str(response.url).rstrip('/')
                    # Ignore redirects to the main page or directory page
                    if curr_url in ["https://www.gov.pl", "https://www.gov.pl/web/dyplomacja/informacje-dla-podrozujacych"]:
                        continue
                    
                    # Basic validation that we are on a travel advisory page
                    if any(kw in response.text.lower() for kw in ["bezpieczeństwo", "ostrzeżenia", "informacje dla podróżujących"]):
                        response_text = response.text
                        final_url = str(response.url)
                        logger.info(f"  - Pattern {i+1} worked: {url}")
                        break 
            except Exception as e: 
                last_status = str(e)
                continue

    if not response_text:
        return {"error": f"No valid MSZ page found for {iso_code}. Last status: {last_status}"}

    soup = BeautifulSoup(response_text, 'html.parser')
    risk_level = "low"
    
    # Risk extraction
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
    
    # Text summary extraction
    risk_summary = ""
    summary_container = soup.select_one('.editor-content')
    if summary_container:
        # Usually the first paragraph or strong text is the risk summary
        first_p = summary_container.select_one('p')
        if first_p:
            risk_summary = first_p.get_text().strip()
    
    if not risk_summary:
        risk_summary = f"MSZ zaleca {risk_level} poziom ostrożności podczas podróży do tego kraju ({country.name_pl or country.name})."

    # Save to database
    safety = db.query(models.SafetyInfo).filter(models.SafetyInfo.country_id == country.id).first()
    if not safety:
        safety = models.SafetyInfo(country_id=country.id)
        db.add(safety)
    
    safety.risk_level = risk_level
    safety.summary = risk_summary
    safety.full_url = final_url
    safety.last_checked = func.now()
    
    db.commit()
    return {"status": "success", "risk": risk_level}
    page_text = soup.get_text().lower()
    if 'odradza wszelkie podróże' in page_text or 'odradzamy wszelkie podróże' in page_text: 
        risk_level = 'critical'
    elif risk_level == 'low':
        if 'odradza podróże, które nie są konieczne' in page_text or 'odradzamy podróże, które nie są konieczne' in page_text: 
            risk_level = 'high'
        elif 'zachowanie szczególnej ostrożności' in page_text or 'zachowaj szczególną ostrożność' in page_text: 
            risk_level = 'medium'

    country_name = country.name_pl
    if risk_level == 'critical':
        risk_phrase = f"MSZ odradza wszelkie podróże do tego kraju ({country_name})."
    elif risk_level == 'high':
        risk_phrase = f"MSZ odradza podróże, które nie są konieczne do tego kraju ({country_name})."
    elif risk_level == 'medium':
        risk_phrase = f"MSZ zaleca zachowanie szczególnej ostrożności podczas podróży do tego kraju ({country_name})."
    else:
        risk_phrase = f"MSZ zaleca zachowanie zwykłej ostrożności podczas podróży do tego kraju ({country_name})."

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
    
    safety = db.query(models.SafetyInfo).filter(models.SafetyInfo.country_id == country.id).first()
    if not safety:
        safety = models.SafetyInfo(country_id=country.id)
        db.add(safety)
    safety.risk_level, safety.summary, safety.full_url = risk_level, risk_phrase, final_url
    safety.risk_details = risk_details

    # Entry Requirements
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
        
        if any(x in visa_text.lower() for x in ["nie muszą mieć wizy", "nie jest wymagana wiza", "ruch bezwizowy", "bezwizowo"]):
            visa_req = False
        elif any(x in visa_text.lower() for x in ["wymagana jest wiza", "obowiązek wizowy"]):
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

    # Health
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
            if v.lower() in health_text_lower: suggested_list.append(v)
        
        if suggested_list: vaccines_sug = "Zalecane: " + ", ".join(suggested_list)

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
                logger.warning(f"  - Skip: {res['error']}")
                results["details"].append(f"{country.iso_alpha2}: {res['error']}")
            elif res.get("status") == "skipped":
                results["success"] += 1
                logger.info(f"  - Skipped: {res.get('reason')}")
            else: 
                results["success"] += 1
                logger.info(f"  - OK: Risk {res.get('risk_level', 'unknown')}")
            
            await asyncio.sleep(1.0) 
        except Exception as e:
            results["errors"] += 1
            err_msg = f"{country.iso_alpha2} CRITICAL: {str(e)}"
            results["details"].append(err_msg)
            logger.error(f"  - {err_msg}")
            
    return results
