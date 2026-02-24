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

# Manual mapping for countries and their subdomains on gov.pl
MANUAL_MAPPING = {
    'AF': 'afganistan', 'AL': 'albania', 'DZ': 'algieria', 'AD': 'andora', 'AO': 'angola', 
    'AR': 'argentyna', 'AM': 'armenia', 'AU': 'australia', 'AT': 'austria', 'AZ': 'azerbejdzan',
    'BS': 'bahamy', 'BH': 'bahrajn', 'BD': 'bangladesz', 'BB': 'barbados', 'BE': 'belgia',
    'BZ': 'belize', 'BJ': 'benin', 'BT': 'bhutan', 'BY': 'bialorus', 'BO': 'boliwia',
    'BA': 'bosnia-i-hercegowina', 'BW': 'botswana', 'BR': 'brazylia', 'BN': 'brunei-darussalam', 'BG': 'bulgaria',
    'BF': 'burkina-faso', 'BI': 'burundi', 'CL': 'chile', 'CN': 'chiny', 'HR': 'chorwacja',
    'CY': 'cypr', 'TD': 'czad', 'CZ': 'czechy', 'DK': 'dania', 'DM': 'dominika',
    'DO': 'dominikana', 'DJ': 'dzibuti', 'EG': 'egipt', 'EC': 'ekwador', 'ER': 'erytrea',
    'EE': 'estonia', 'ET': 'etiopia', 'PH': 'filipiny', 'FI': 'finlandia', 'FR': 'francja',
    'GA': 'gabon', 'GM': 'gambia', 'GH': 'ghana', 'GR': 'grecja', 'GD': 'grenada',
    'GE': 'gruzja', 'GY': 'gujana', 'GN': 'gwinea', 'GW': 'gwineabissau', 'GQ': 'gwinearownikowa',
    'HT': 'haiti', 'ES': 'hiszpania', 'NL': 'holandia', 'HN': 'honduras', 'IN': 'indie',
    'ID': 'indonezja', 'IQ': 'irak', 'IR': 'iran', 'IE': 'irlandia', 'IS': 'islandia',
    'IL': 'izrael', 'JM': 'jamajka', 'JP': 'japonia', 'YE': 'jemen', 'JO': 'jordania',
    'KH': 'kambodza', 'CM': 'kamerun', 'CA': 'kanada', 'QA': 'katar', 'KZ': 'kazachstan',
    'KE': 'kenia', 'KG': 'kirgistan', 'CO': 'kolumbia', 'KM': 'komory', 'CG': 'kongo',
    'CD': 'demokratyczna-republika-kong', 'KP': 'korea-polnocna', 'KR': 'republika-korei', 'XK': 'kosowo', 'CR': 'kostaryka',
    'CU': 'kuba', 'KW': 'kuwejt', 'LA': 'laos', 'LS': 'lesotho', 'LB': 'liban',
    'LR': 'liberia', 'LY': 'libia', 'LI': 'liechtenstein', 'LT': 'litwa', 'LU': 'luksemburg',
    'LV': 'lotwa', 'MK': 'macedonia-polnocna', 'MG': 'madagaskar', 'MY': 'malezja', 'MW': 'malawi',
    'MV': 'malediwy', 'ML': 'bamako', 'MT': 'malta', 'MA': 'maroko', 'MR': 'mauretania',
    'MU': 'mauritius', 'MX': 'meksyk', 'MD': 'moldawia', 'MC': 'monako', 'MN': 'mongolia',
    'ME': 'czarnogora', 'MZ': 'mozambik', 'MM': 'mjanma', 'NA': 'namibia', 'NP': 'nepal',
    'DE': 'niemcy', 'NE': 'niger', 'NG': 'nigeria', 'NI': 'nikaragua', 'NO': 'norwegia',
    'NZ': 'nowa-zelandia', 'OM': 'oman', 'PK': 'pakistan', 'PA': 'panama', 'PG': 'papua-nowa-gwinea',
    'PY': 'paragwaj', 'PE': 'peru', 'PT': 'portugalia', 'RU': 'rosja', 'RW': 'rwanda',
    'RO': 'rumunia', 'SV': 'salwador', 'WS': 'samoa', 'SM': 'san-marino', 'SA': 'arabia-saudyjska',
    'SN': 'senegal', 'RS': 'serbia', 'SC': 'seszele', 'SL': 'sierraleone', 'SG': 'singapur',
    'SK': 'slowacja', 'SI': 'slowenia', 'SO': 'somalia', 'LK': 'srilanka', 'US': 'usa',
    'SD': 'sudan', 'SR': 'surinam', 'SY': 'syria', 'SZ': 'suazi', 'TJ': 'tadzykistan',
    'TH': 'tajlandia', 'TW': 'tajwan', 'TZ': 'tanzania', 'TL': 'timor-wschodni', 'TG': 'togo',
    'TO': 'tonga', 'TT': 'trynidaditobago', 'TN': 'tunezja', 'TR': 'turcja', 'TM': 'turkmenistan',
    'UG': 'uganda', 'UA': 'ukraina', 'UY': 'urugwaj', 'UZ': 'uzbekistan', 'VU': 'vanuatu',
    'VA': 'watykan', 'VE': 'wenezuela', 'HU': 'wegry', 'GB': 'wielkabrytania', 'VN': 'wietnam',
    'IT': 'wlochy', 'CI': 'wybrzeze-kosci-sloniowej', 'ZM': 'zambia', 'ZW': 'zimbabwe',
    'AE': 'zjednoczone-emiraty-arabskie'
}

def clean_name(name):
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
    slug = _SLUG_CACHE.get(name_pl) or MANUAL_MAPPING.get(iso_code.upper())
    
    if not slug:
        slug = name_pl.replace(' ', '').replace('ą', 'a').replace('ć', 'c').replace('ę', 'e').replace('ł', 'l').replace('ń', 'n').replace('ó', 'o').replace('ś', 's').replace('ź', 'z').replace('ż', 'z')
        slug = re.sub(r'[^a-z0-9]', '', slug)

    urls_to_try = [
        f"https://www.gov.pl/web/dyplomacja/{slug}",
        f"https://www.gov.pl/web/{slug}/idp",
        f"https://www.gov.pl/web/{slug}/informacje-dla-podrozujacych",
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

    # Extract additional details (all alerts and travel advisory descriptions)
    risk_details_list = []
    
    # Priority 1: Main travel advisory description
    advisory_el = soup.select_one('.travel-advisory--description')
    if advisory_el:
        risk_details_list.append(advisory_el.get_text().strip())
        
    # Priority 2: Other alerts (alert-danger, alert-info)
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
    vaccines_req, vaccines_sug = "", ""
    health_section = soup.find(string=re.compile(r'^Zdrowie$', re.I)) or soup.find(string=re.compile(r'Informacje dotyczące zdrowia', re.I))
    if health_section:
        health_text = ""
        curr = health_section.parent
        # Look ahead for a few paragraphs or until next major header
        for _ in range(12):
            if curr:
                txt = curr.get_text().strip()
                if txt: health_text += txt + "\n"
                curr = curr.find_next_sibling()
                if curr and curr.name in ['h2', 'h3']: break
        
        # Simple extraction logic
        # Required usually mentions "szczepienia obowiązkowe" or "żółta febra"
        if "żółtą febrę" in health_text.lower() or "żółtej febry" in health_text.lower():
            if "obowiązkowe" in health_text.lower() or "wymagane" in health_text.lower():
                vaccines_req = "Szczepienie przeciw żółtej febrze (wymagane w określonych sytuacjach)"
        
        # Suggested usually lists many diseases
        suggested_list = []
        for v in ["tężec", "błonica", "krztusiec", "dur brzuszny", "WZW A", "WZW B", "wścieklizna", "cholera", "polio"]:
            if v.lower() in health_text.lower():
                suggested_list.append(v)
        
        if suggested_list:
            vaccines_sug = "Zalecane szczepienia: " + ", ".join(suggested_list)
        else:
            # Fallback: take first 200 chars if something was found but not matched
            if health_text.strip():
                vaccines_sug = health_text.strip()[:300] + "..."

    practical = db.query(models.PracticalInfo).filter(models.PracticalInfo.country_id == country.id).first()
    if not practical:
        practical = models.PracticalInfo(country_id=country.id)
        db.add(practical)
    practical.vaccinations_required = vaccines_req
    practical.vaccinations_suggested = vaccines_sug

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
