import httpx
from bs4 import BeautifulSoup
from sqlalchemy.orm import Session
from .. import models, crud
import asyncio
import re
import logging

logger = logging.getLogger("uvicorn")

# Manual mapping for countries that are hard to guess or have unique subdomains
# This is our source of truth for the core country subdomains on gov.pl
MANUAL_MAPPING = {
    'AF': 'afganistan', 'AL': 'albania', 'DZ': 'algieria', 'AD': 'andora', 'AO': 'angola', 
    'AR': 'argentyna', 'AM': 'armenia', 'AU': 'australia', 'AT': 'austria', 'AZ': 'azerbejdzan',
    'BS': 'bahamy', 'BH': 'bahrajn', 'BD': 'bangladesz', 'BB': 'barbados', 'BE': 'belgia',
    'BZ': 'belize', 'BJ': 'benin', 'BT': 'bhutan', 'BY': 'bialorus', 'BO': 'boliwia',
    'BA': 'bosnia-i-hercegowina', 'BW': 'botswana', 'BR': 'brazylia', 'BN': 'brunei', 'BG': 'bulgaria',
    'BF': 'burkina-faso', 'BI': 'burundi', 'CL': 'chile', 'CN': 'chiny', 'HR': 'chorwacja',
    'CY': 'cypr', 'TD': 'czad', 'CZ': 'czechy', 'DK': 'dania', 'DM': 'dominika',
    'DO': 'dominikana', 'DJ': 'dzibuti', 'EG': 'egipt', 'EC': 'ekwador', 'ER': 'erytrea',
    'EE': 'estonia', 'ET': 'etiopia', 'PH': 'filipiny', 'FI': 'finlandia', 'FR': 'francja',
    'GA': 'gabon', 'GM': 'gambia', 'GH': 'ghana', 'GR': 'grecja', 'GD': 'grenada',
    'GE': 'gruzja', 'GY': 'gujana', 'GN': 'gwinea', 'GW': 'gwinea-bissau', 'GQ': 'gwinea-rownikowa',
    'HT': 'haiti', 'ES': 'hiszpania', 'NL': 'holandia', 'HN': 'honduras', 'IN': 'indie',
    'ID': 'indonezja', 'IQ': 'irak', 'IR': 'iran', 'IE': 'irlandia', 'IS': 'islandia',
    'IL': 'izrael', 'JM': 'jamajka', 'JP': 'japonia', 'YE': 'jemen', 'JO': 'jordania',
    'KH': 'kambodza', 'CM': 'kamerun', 'CA': 'kanada', 'QA': 'katar', 'KZ': 'kazachstan',
    'KE': 'kenia', 'KG': 'kirgistan', 'CO': 'kolumbia', 'KM': 'komory', 'CG': 'kongo',
    'CD': 'demokratyczna-republika-konga', 'KP': 'korea-polnocna', 'KR': 'republika-korei', 'XK': 'kosowo', 'CR': 'kostaryka',
    'CU': 'kuba', 'KW': 'kuwejt', 'LA': 'laos', 'LS': 'lesotho', 'LB': 'liban',
    'LR': 'liberia', 'LY': 'libia', 'LI': 'liechtenstein', 'LT': 'litwa', 'LU': 'luksemburg',
    'LV': 'lotwa', 'MK': 'macedonia-polnocna', 'MG': 'madagaskar', 'MY': 'malezja', 'MW': 'malawi',
    'MV': 'malediwy', 'ML': 'mali', 'MT': 'malta', 'MA': 'maroko', 'MR': 'mauretania',
    'MU': 'mauritius', 'MX': 'meksyk', 'MD': 'moldawia', 'MC': 'monako', 'MN': 'mongolia',
    'ME': 'czarnogora', 'MZ': 'mozambik', 'MM': 'mjanma', 'NA': 'namibia', 'NP': 'nepal',
    'DE': 'niemcy', 'NE': 'niger', 'NG': 'nigeria', 'NI': 'nikaragua', 'NO': 'norwegia',
    'NZ': 'nowa-zelandia', 'OM': 'oman', 'PK': 'pakistan', 'PA': 'panama', 'PG': 'papua-nowa-gwinea',
    'PY': 'paragwaj', 'PE': 'peru', 'PT': 'portugalia', 'RU': 'rosja', 'RW': 'rwanda',
    'RO': 'rumunia', 'SV': 'salwador', 'WS': 'samoa', 'SM': 'san-marino', 'SA': 'arabia-saudyjska',
    'SN': 'senegal', 'RS': 'serbia', 'SC': 'seszele', 'SL': 'sierra-leone', 'SG': 'singapur',
    'SK': 'slowacja', 'SI': 'slowenia', 'SO': 'somalia', 'LK': 'sri-lanka', 'US': 'usa',
    'SD': 'sudan', 'SR': 'surinam', 'SY': 'syria', 'SZ': 'suazi', 'TJ': 'tadzykistan',
    'TH': 'tajlandia', 'TW': 'tajwan', 'TZ': 'tanzania', 'TL': 'timor-wschodni', 'TG': 'togo',
    'TO': 'tonga', 'TT': 'trynidad-i-tobago', 'TN': 'tunezja', 'TR': 'turcja', 'TM': 'turkmenistan',
    'UG': 'uganda', 'UA': 'ukraina', 'UY': 'urugwaj', 'UZ': 'uzbekistan', 'VU': 'vanuatu',
    'VA': 'watykan', 'VE': 'wenezuela', 'HU': 'wegry', 'GB': 'wielka-brytania', 'VN': 'wietnam',
    'IT': 'wlochy', 'CI': 'wybrzeze-kosci-sloniowej', 'ZM': 'zambia', 'ZW': 'zimbabwe',
    'AE': 'zjednoczone-emiraty-arabskie'
}

async def scrape_country(db: Session, iso_code: str):
    """Scrape MSZ data for specific country"""
    if iso_code == 'PL':
        return {"status": "skipped", "reason": "Home country"}

    country = crud.get_country_by_iso2(db, iso_code)
    if not country:
        return {"error": "Country not found in DB"}

    name_pl = country.name_pl.lower() if country.name_pl else country.name.lower()
    slug = MANUAL_MAPPING.get(iso_code.upper())
    
    if not slug:
        # Fallback slug generation
        slug = name_pl.replace(' ', '').replace('ą', 'a').replace('ć', 'c').replace('ę', 'e').replace('ł', 'l').replace('ń', 'n').replace('ó', 'o').replace('ś', 's').replace('ź', 'z').replace('ż', 'z')
        slug = re.sub(r'[^a-z0-9]', '', slug)

    # Strategy: Priority list of URLs
    urls_to_try = [
        f"https://www.gov.pl/web/{slug}/idp", # Direct country site
        f"https://www.gov.pl/web/{slug}/informacje-dla-podrozujacych",
        f"https://www.gov.pl/web/dyplomacja/informacje-dla-podrozujacych/{slug}", # Main diplomacy path
    ]

    # Handle cases where slug might be slightly different
    slug_hyphen = slug.replace('', '-').strip('-') # This is just a placeholder logic
    # Real logic for common hyphen discrepancy
    if '-' not in slug:
        # Try with hyphens for some specific cases if manual mapping was missing them
        pass

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    response_text = None
    final_url = None

    async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
        for url in urls_to_try:
            try:
                response = await client.get(url, headers=headers)
                # STRICT REDIRECT CHECK: Gov.pl redirects 404s to its home page
                if response.status_code == 200:
                    curr_url = str(response.url).rstrip('/')
                    if curr_url == "https://www.gov.pl":
                        continue
                    
                    # Content validation: must contain travel-related keywords
                    text_lower = response.text.lower()
                    if "bezpieczeństwo" in text_lower or "informacje dla podróżujących" in text_lower:
                        response_text = response.text
                        final_url = str(response.url)
                        break
            except:
                continue

    if not response_text:
        return {"error": f"Failed to find valid MSZ page for {iso_code}"}

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
        # Keyword detection in the whole page
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
                if txt and "Odyseusz" not in txt and "placówką zagraniczną RP" not in txt:
                    paragraphs.append(txt)
                count += 1
            elif curr.name == 'div':
                # Sometimes gov.pl wraps paragraphs in divs
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

    # Update DB
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
                results["success"] += 1 # Counting skip as success for logic flow
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
