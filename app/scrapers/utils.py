import re
import logging
import os
from deep_translator import GoogleTranslator
import httpx
import asyncio
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

logger = logging.getLogger("uvicorn")

# Manual mapping for countries and their subdomains on gov.pl
MSZ_GOV_PL_MANUAL_MAPPING = {
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
    'KE': 'kenia', 'KG': 'kirgistan', 'CO': 'kolumbia', 'KM': 'komory', 'CG': 'kongo-brazzaville',
    'CD': 'kongo-kinszasa', 'KP': 'korea-polnocna', 'KR': 'republika-korei', 'XK': 'kosowo', 'CR': 'kostaryka',
    'CU': 'kuba', 'KW': 'kuwejt', 'LA': 'laos', 'LS': 'lesotho', 'LB': 'liban',
    'LR': 'liberia', 'LY': 'libia', 'LI': 'liechtenstein', 'LT': 'litwa', 'LU': 'luksemburg',
    'LV': 'lotwa', 'MK': 'macedonia-polnocna', 'MG': 'madagaskar', 'MY': 'malezja', 'MW': 'malawi',
    'MV': 'malediwy', 'ML': 'bamako', 'MT': 'malta', 'MA': 'maroko', 'MR': 'maputo',
    'MU': 'mauritius', 'MX': 'meksyk', 'MD': 'moldawia', 'MC': 'monako', 'MN': 'mongolia',
    'ME': 'czarnogora', 'MZ': 'mozambik', 'MM': 'mjanma', 'NA': 'namibia', 'NP': 'nepal',
    'DE': 'niemcy', 'NE': 'niger', 'NG': 'nigeria', 'NI': 'nikaragua', 'NO': 'norwegia',
    'NZ': 'nowa-zelandia', 'OM': 'oman', 'PK': 'pakistan', 'PA': 'panama', 'PG': 'papua-nowa-gwinea',
    'PY': 'paragwaj', 'PE': 'peru', 'PT': 'portugalia', 'RU': 'rosja', 'RW': 'rwanda',
    'RO': 'rumunia', 'SV': 'salwador', 'WS': 'samoa', 'SM': 'san-marino', 'SA': 'arabia-saudyjska',
    'SN': 'senegal', 'RS': 'serbia', 'SC': 'seszele', 'SL': 'sierraleone', 'SG': 'singapur',
    'SK': 'slowacja', 'SI': 'slowenia', 'SO': 'somalia', 'LK': 'srilanka', 'US': 'usa',
    'SD': 'sudan', 'SR': 'surinam', 'SY': 'syria', 'SZ': 'eswatini', 'TJ': 'tadzykistan',
    'TH': 'tajlandia', 'TW': 'tajwan', 'TZ': 'tanzania', 'TL': 'timor-wschodni', 'TG': 'togo',
    'TO': 'tonga', 'TT': 'trynidaditobago', 'TN': 'tunezja', 'TR': 'turcja', 'TM': 'turkmenistan',
    'UG': 'uganda', 'UA': 'ukraina', 'UY': 'urugwaj', 'UZ': 'uzbekistan', 'VU': 'vanuatu',
    'VA': 'watykan', 'VE': 'wenezuela', 'HU': 'wegry', 'GB': 'wielkabrytania', 'VN': 'wietnam',
    'IT': 'wlochy', 'CI': 'wybrzeze-kosci-sloniowej', 'ZM': 'zambia', 'ZW': 'zimbabwe',
    'AE': 'zjednoczone-emiraty-arabskie'
}

CDC_MAPPING = {
    'RU': 'russia', 'US': 'united-states', 'GB': 'united-kingdom',
    'KR': 'south-korea', 'KP': 'north-korea', 'AE': 'united-arab-emirates',
    'CD': 'democratic-republic-of-the-congo', 'CG': 'republic-of-the-congo',
    'CI': 'cote-divoire', 'SZ': 'eswatini'
}

WIKI_NAME_MAP = {
    "Congo (Democratic Republic of)": "CD",
    "Congo (Republic of)": "CG",
    "Democratic Republic of the Congo": "CD",
    "Republic of the Congo": "CG",
    "DR Congo": "CD",
    "Congo": "CG"
}

# Known translation fixes for common automated errors
CURRENCY_FIXES = {
    "Brazilian real": "Real brazylijski",
    "Brazylijski prawdziwy": "Real brazylijski",
    "Prawdziwy brazylijski": "Real brazylijski",
    "Prawdziw brazylijski": "Real brazylijski",
    "South African rand": "Rand południowoafrykański",
    "United States dollar": "Dolar amerykański",
    "Euro": "Euro",
    "British pound": "Funt brytyjski",
    "Polish złoty": "Złoty polski",
    "Złoty": "Złoty",
    "North Korean won": "Won północnokoreański",
    "South Korean won": "Won południowokoreański",
    "zwyciężyła": "Won",
    "zwycięzca": "Won",
    "Korea Północna zwyciężyła": "Won północnokoreański",
    "Korea Południowa zwyciężyła": "Won południowokoreański"
}

# In-memory cache for translations to avoid redundant API calls
_TRANSLATION_CACHE = {}

def translate_to_pl(text: str) -> str:
    if not text: return text
    if text in CURRENCY_FIXES: return CURRENCY_FIXES[text]
    if text in _TRANSLATION_CACHE: return _TRANSLATION_CACHE[text]
    try:
        translated = GoogleTranslator(source='auto', target='pl').translate(text)
        translated = normalize_polish_text(translated)
        if translated in CURRENCY_FIXES: translated = CURRENCY_FIXES[translated]
        _TRANSLATION_CACHE[text] = translated
        return translated
    except Exception as e:
        logger.error(f"Translation error for '{text}': {e}")
        return text

def normalize_polish_text(text: str) -> str:
    if not text: return text
    text = text.replace("WybrzeŻe", "Wybrzeże").replace("WYBRZEŻE", "Wybrzeże")
    text = text.replace("Suazi", "Eswatini").replace("SUAZI", "ESWATINI")
    text = text.replace(" .", ".").replace(" ,", ",")
    return text.strip()

def clean_polish_name(name: str) -> str:
    if not name: return ""
    name = re.sub(r'\(.*?\)', '', name)
    name = name.split(',')[0]
    return name.strip().lower()

def slugify(text: str) -> str:
    if not text: return ""
    text = text.lower()
    polish_chars = str.maketrans("ąćęłńóśźż", "acelnoszz")
    text = text.translate(polish_chars)
    text = re.sub(r'[^a-z0-9\s-]', '', text)
    text = re.sub(r'[\s]+', '-', text)
    return text.strip('-')

def get_headers():
    headers = {
        "User-Agent": "TravelSheet/1.1 (https://github.com/zyngi/TravelSheet; contact@travelsheet.io)",
        "Accept": "application/json"
    }
    # Add Wikimedia Access Token if available
    access_token = os.getenv("WIKIMEDIA_ACCESS_TOKEN")
    if access_token and "twoj_" not in access_token:
        headers["Authorization"] = f"Bearer {access_token}"
    return headers

async def async_get(url: str, params: dict = None, headers: dict = None, timeout: float = 30.0):
    combined_headers = get_headers()
    if headers: combined_headers.update(headers)
    async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
        try:
            response = await client.get(url, params=params, headers=combined_headers)
            response.raise_for_status()
            return response
        except Exception as e:
            logger.error(f"HTTP Error for {url}: {e}")
            return None

# Global semaphore to limit concurrent SPARQL requests to Wikidata
# This helps prevent 504 timeouts by not overwhelming the server
_WIKIDATA_SEMAPHORE = asyncio.Semaphore(1) 
_WIKIDATA_DOWN = False # Global flag to skip Wikidata if it's struggling

async def async_sparql_get(query: str, description: str = "SPARQL"):
    """Robust SPARQL query helper with retries and exponential backoff"""
    global _WIKIDATA_DOWN
    if _WIKIDATA_DOWN:
        return []

    url = "https://query.wikidata.org/sparql"
    headers = get_headers()
    headers["Content-Type"] = "application/x-www-form-urlencoded"
    headers["Accept"] = "application/sparql-results+json"
    
    max_retries = 2 # Reduced retries during struggle
    base_delay = 5
    
    for attempt in range(max_retries):
        try:
            async with _WIKIDATA_SEMAPHORE:
                async with httpx.AsyncClient(timeout=60.0) as client: # Reduced timeout to fail faster
                    resp = await client.post(url, data={'query': query}, headers=headers)
                    
                    if resp.status_code == 200:
                        return resp.json().get("results", {}).get("bindings", [])
                    
                    elif resp.status_code == 429:
                        delay = base_delay * (2 ** attempt)
                        logger.warning(f"Wikidata Rate Limit hit ({description}), retrying in {delay}s...")
                        await asyncio.sleep(delay)
                        
                    elif resp.status_code in [504, 502, 503]:
                        logger.error(f"Wikidata Server Error {resp.status_code} ({description}).")
                        if attempt == max_retries - 1:
                            logger.error("Wikidata seems to be down or overloaded. Marking as DOWN for this session.")
                            _WIKIDATA_DOWN = True
                        await asyncio.sleep(base_delay)
                    else:
                        logger.error(f"Wikidata error {resp.status_code} for {description}: {resp.text[:200]}")
                        break
        except Exception as e:
            logger.error(f"SPARQL request error for {description}: {e}")
            if attempt == max_retries - 1:
                _WIKIDATA_DOWN = True
            await asyncio.sleep(2)
                
    return []
