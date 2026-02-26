import re
import logging
from deep_translator import GoogleTranslator

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
    'SD': 'sudan', 'SR': 'surinam', 'SY': 'syria', 'SZ': 'suazi', 'TJ': 'tadzykistan',
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
    "Złoty": "Złoty"
}

# In-memory cache for translations to avoid redundant API calls
_TRANSLATION_CACHE = {}

def translate_to_pl(text: str) -> str:
    if not text: return text
    
    # Check for known fixes first
    if text in CURRENCY_FIXES:
        return CURRENCY_FIXES[text]
    
    if text in _TRANSLATION_CACHE:
        return _TRANSLATION_CACHE[text]
    
    try:
        translated = GoogleTranslator(source='auto', target='pl').translate(text)
        translated = normalize_polish_text(translated) # Clean up translation
        
        # Check if translation result is in fixes
        if translated in CURRENCY_FIXES:
            translated = CURRENCY_FIXES[translated]
            
        _TRANSLATION_CACHE[text] = translated
        return translated
    except Exception as e:
        logger.error(f"Translation error for '{text}': {e}")
        return text

def normalize_polish_text(text: str) -> str:
    """Fix common errors in Polish text/names from external APIs or scrapers."""
    if not text: return text
    
    # Specific fix for Ivory Coast capitalization issue
    text = text.replace("WybrzeŻe", "Wybrzeże")
    text = text.replace("WYBRZEŻE", "Wybrzeże")
    
    # Fix common spacing/punctuation issues from translations
    text = text.replace(" .", ".")
    text = text.replace(" ,", ",")
    
    return text.strip()

def clean_polish_name(name: str) -> str:
    if not name: return ""
    name = re.sub(r'\(.*?\)', '', name)
    name = name.split(',')[0]
    return name.strip().lower()

def slugify(text: str) -> str:
    if not text: return ""
    text = text.lower()
    # Polish characters replacement
    polish_chars = str.maketrans("ąćęłńóśźż", "acelnoszz")
    text = text.translate(polish_chars)
    # Remove non-alphanumeric chars
    text = re.sub(r'[^a-z0-9\s-]', '', text)
    # Replace spaces with hyphens
    text = re.sub(r'[\s]+', '-', text)
    return text.strip('-')

def get_headers():
    return {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json"
    }
