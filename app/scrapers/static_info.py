from sqlalchemy.orm import Session
from sqlalchemy import func
from .. import models
import logging

logger = logging.getLogger("uvicorn")

# Baza danych technicznych i praktycznych (Napięcie, Częstotliwość, Sklepy, eSIM)
# Dane pogrupowane regionalnie dla łatwiejszego zarządzania i fallbacków
REGIONAL_DEFAULTS = {
    'Europe': {
        'voltage': 230, 'freq': 50, 
        'hours': 'Sklepy: 09:00-20:00 (często zamknięte w niedziele)', 
        'esim': True, 'internet': 'Bardzo dobry, powszechne Wi-Fi i 5G.'
    },
    'Asia': {
        'voltage': 220, 'freq': 50, 
        'hours': 'Sklepy: 10:00-22:00 (otwarte codziennie)', 
        'esim': True, 'internet': 'Dobry w miastach, słabszy na prowincji. Tanie karty SIM.'
    },
    'Americas': {
        'voltage': 120, 'freq': 60, 
        'hours': 'Sklepy: 09:00-21:00 (duże centra handlowe do 22:00)', 
        'esim': True, 'internet': 'Powszechny, szybki w dużych miastach.'
    },
    'Africa': {
        'voltage': 230, 'freq': 50, 
        'hours': 'Sklepy: 08:00-18:00 (zależnie od lokalnych warunków)', 
        'esim': False, 'internet': 'Zmienny, najlepiej kupić lokalną kartę SIM.'
    },
    'Oceania': {
        'voltage': 230, 'freq': 50, 
        'hours': 'Sklepy: 09:00-17:30 (centra do 21:00 w czwartki/piątki)', 
        'esim': True, 'internet': 'Dobry, ale drogi poza miastami.'
    }
}

# Specyficzne dane dla krajów (nadpisują regionalne)
TECH_DATA = {
    'US': {'plugs': 'A, B', 'side': 'right', 'voltage': 120, 'freq': 60},
    'CA': {'plugs': 'A, B', 'side': 'right', 'voltage': 120, 'freq': 60},
    'JP': {'plugs': 'A, B', 'side': 'left', 'voltage': 100, 'freq': 50}, # 50/60 mix but 100V
    'PL': {'plugs': 'C, E', 'side': 'right', 'voltage': 230, 'freq': 50},
    'GB': {'plugs': 'G', 'side': 'left', 'voltage': 230, 'freq': 50},
    'TH': {'plugs': 'A, B, C, O', 'side': 'left', 'voltage': 220, 'freq': 50, 'hours': 'Sklepy: 10:00-22:00 (7 dni w tygodniu)'},
    'AE': {'plugs': 'G', 'side': 'right', 'voltage': 230, 'freq': 50, 'hours': 'Sklepy: 10:00-22:00 (często do północy)'},
    'BR': {'plugs': 'N', 'side': 'right', 'voltage': 127, 'freq': 60}, # Some regions 220V
    'AU': {'plugs': 'I', 'side': 'left', 'voltage': 230, 'freq': 50},
    # ... reszta (plugs/side) pozostaje taka sama jak w Twojej bazie, dodajemy tylko nowe pola tam gdzie znane
}

# Skopiowane z poprzedniej wersji dla zachowania ciągłości plugs/side
LEGACY_TECH_DATA = {
    'AF': {'plugs': 'C, F', 'side': 'right'}, 'AL': {'plugs': 'C, F', 'side': 'right'},
    'DZ': {'plugs': 'C, F', 'side': 'right'}, 'AS': {'plugs': 'A, B, I', 'side': 'right'},
    'AD': {'plugs': 'C, F', 'side': 'right'}, 'AO': {'plugs': 'C', 'side': 'right'},
    'AI': {'plugs': 'A, B', 'side': 'left'}, 'AQ': {'plugs': 'C, F', 'side': 'right'},
    'AG': {'plugs': 'A, B', 'side': 'left'}, 'AR': {'plugs': 'C, I', 'side': 'right'},
    'AM': {'plugs': 'C, F', 'side': 'right'}, 'AW': {'plugs': 'A, B, F', 'side': 'right'},
    'AU': {'plugs': 'I', 'side': 'left'}, 'AT': {'plugs': 'C, F', 'side': 'right'},
    'AZ': {'plugs': 'C, F', 'side': 'right'}, 'BS': {'plugs': 'A, B', 'side': 'left'},
    'BH': {'plugs': 'G', 'side': 'left'}, 'BD': {'plugs': 'A, C, G, K', 'side': 'left'},
    'BB': {'plugs': 'A, B', 'side': 'left'}, 'BY': {'plugs': 'C, F', 'side': 'right'},
    'BE': {'plugs': 'C, E', 'side': 'right'}, 'BZ': {'plugs': 'A, B, G', 'side': 'right'},
    'BJ': {'plugs': 'C, E', 'side': 'right'}, 'BM': {'plugs': 'A, B', 'side': 'left'},
    'BT': {'plugs': 'C, D, G', 'side': 'left'}, 'BO': {'plugs': 'A, C', 'side': 'right'},
    'BA': {'plugs': 'C, F', 'side': 'right'}, 'BW': {'plugs': 'D, G, M', 'side': 'left'},
    'BR': {'plugs': 'N', 'side': 'right'}, 'BN': {'plugs': 'G', 'side': 'left'},
    'BG': {'plugs': 'C, F', 'side': 'right'}, 'BF': {'plugs': 'C, E', 'side': 'right'},
    'BI': {'plugs': 'C, E', 'side': 'right'}, 'BQ': {'plugs': 'A, B', 'side': 'right'},
    'KH': {'plugs': 'A, C, G', 'side': 'right'},
    'CM': {'plugs': 'C, E', 'side': 'right'}, 'CA': {'plugs': 'A, B', 'side': 'right'},
    'CV': {'plugs': 'C, F', 'side': 'right'}, 'KY': {'plugs': 'A, B', 'side': 'left'},
    'CF': {'plugs': 'C, E', 'side': 'right'}, 'TD': {'plugs': 'C, E, F', 'side': 'right'},
    'CL': {'plugs': 'C, L', 'side': 'right'}, 'CN': {'plugs': 'A, C, I', 'side': 'right'},
    'CO': {'plugs': 'A, B', 'side': 'right'}, 'KM': {'plugs': 'C, E', 'side': 'right'},
    'CG': {'plugs': 'C, E', 'side': 'right'}, 'CD': {'plugs': 'C, E', 'side': 'right'},
    'CK': {'plugs': 'I', 'side': 'left'}, 'CR': {'plugs': 'A, B', 'side': 'right'},
    'CI': {'plugs': 'C, E', 'side': 'right'}, 'HR': {'plugs': 'C, F', 'side': 'right'},
    'CU': {'plugs': 'A, B, C, L', 'side': 'right'}, 'CW': {'plugs': 'A, B', 'side': 'right'},
    'CY': {'plugs': 'G', 'side': 'left'}, 'CZ': {'plugs': 'C, E', 'side': 'right'},
    'DK': {'plugs': 'C, E, F, K', 'side': 'right'}, 'DJ': {'plugs': 'C, E', 'side': 'right'},
    'DM': {'plugs': 'D, G', 'side': 'left'}, 'DO': {'plugs': 'A, B', 'side': 'right'},
    'EC': {'plugs': 'A, B', 'side': 'right'}, 'EG': {'plugs': 'C, F', 'side': 'right'},
    'SV': {'plugs': 'A, B', 'side': 'right'}, 'GQ': {'plugs': 'C, E', 'side': 'right'},
    'ER': {'plugs': 'C, L', 'side': 'right'}, 'EE': {'plugs': 'C, F', 'side': 'right'},
    'ET': {'plugs': 'C, F', 'side': 'right'}, 'FK': {'plugs': 'G', 'side': 'left'},
    'FO': {'plugs': 'C, E, F, K', 'side': 'right'}, 'FJ': {'plugs': 'I', 'side': 'left'},
    'FI': {'plugs': 'C, F', 'side': 'right'}, 'FR': {'plugs': 'C, E', 'side': 'right'},
    'GF': {'plugs': 'C, E', 'side': 'right'}, 'PF': {'plugs': 'C, E', 'side': 'right'},
    'GA': {'plugs': 'C', 'side': 'right'}, 'GM': {'plugs': 'G', 'side': 'left'},
    'GE': {'plugs': 'C, F', 'side': 'right'}, 'DE': {'plugs': 'C, F', 'side': 'right'},
    'GH': {'plugs': 'D, G', 'side': 'left'}, 'GI': {'plugs': 'C, G', 'side': 'right'},
    'GR': {'plugs': 'C, F', 'side': 'right'}, 'GL': {'plugs': 'C, F, K', 'side': 'right'},
    'GD': {'plugs': 'G', 'side': 'left'}, 'GP': {'plugs': 'C, D, E', 'side': 'right'},
    'GU': {'plugs': 'A, B', 'side': 'right'}, 'GT': {'plugs': 'A, B', 'side': 'right'},
    'GG': {'plugs': 'G', 'side': 'left'}, 'GN': {'plugs': 'C, F, K', 'side': 'right'},
    'GW': {'plugs': 'C', 'side': 'right'}, 'GY': {'plugs': 'A, B, D, G', 'side': 'left'},
    'HT': {'plugs': 'A, B', 'side': 'right'}, 'HN': {'plugs': 'A, B', 'side': 'right'},
    'HK': {'plugs': 'G', 'side': 'left'}, 'HU': {'plugs': 'C, F', 'side': 'right'},
    'IS': {'plugs': 'C, F', 'side': 'right'}, 'IN': {'plugs': 'C, D, M', 'side': 'left'},
    'ID': {'plugs': 'C, F', 'side': 'right'}, 'IR': {'plugs': 'C, F', 'side': 'right'},
    'IQ': {'plugs': 'C, D, G', 'side': 'right'}, 'IE': {'plugs': 'G', 'side': 'left'},
    'IM': {'plugs': 'G', 'side': 'left'}, 'IL': {'plugs': 'C, H, M', 'side': 'right'},
    'IT': {'plugs': 'C, F, L', 'side': 'right'}, 'JM': {'plugs': 'A, B', 'side': 'left'},
    'JP': {'plugs': 'A, B', 'side': 'left'}, 'JE': {'plugs': 'G', 'side': 'left'},
    'JO': {'plugs': 'B, C, D, G, J', 'side': 'right'}, 'KZ': {'plugs': 'C, F', 'side': 'right'},
    'KE': {'plugs': 'G', 'side': 'left'}, 'KI': {'plugs': 'I', 'side': 'left'},
    'KP': {'plugs': 'A, C, F', 'side': 'right'}, 'KR': {'plugs': 'C, F', 'side': 'right'},
    'KW': {'plugs': 'C, G', 'side': 'right'}, 'KG': {'plugs': 'C, F', 'side': 'right'},
    'LA': {'plugs': 'A, B, C, E, F', 'side': 'right'}, 'LV': {'plugs': 'C, F', 'side': 'right'},
    'LB': {'plugs': 'A, B, C, D, G', 'side': 'right'}, 'LS': {'plugs': 'M', 'side': 'left'},
    'LR': {'plugs': 'A, B, C, E, F', 'side': 'right'}, 'LY': {'plugs': 'C, D, F, L', 'side': 'right'},
    'LI': {'plugs': 'C, J', 'side': 'right'}, 'LT': {'plugs': 'C, F', 'side': 'right'},
    'LU': {'plugs': 'C, F', 'side': 'right'}, 'MO': {'plugs': 'D, G, M', 'side': 'left'},
    'MG': {'plugs': 'C, E', 'side': 'right'}, 'MW': {'plugs': 'G', 'side': 'left'},
    'MY': {'plugs': 'G', 'side': 'left'}, 'MV': {'plugs': 'A, C, D, G, J, K, L', 'side': 'left'},
    'ML': {'plugs': 'C, E', 'side': 'right'}, 'MT': {'plugs': 'G', 'side': 'left'},
    'MH': {'plugs': 'A, B', 'side': 'right'}, 'MQ': {'plugs': 'C, D, E', 'side': 'right'},
    'MR': {'plugs': 'C', 'side': 'right'}, 'MU': {'plugs': 'C, G', 'side': 'left'},
    'YT': {'plugs': 'C, E', 'side': 'right'}, 'MX': {'plugs': 'A, B', 'side': 'right'},
    'MD': {'plugs': 'C, F', 'side': 'right'}, 'MC': {'plugs': 'C, E, F', 'side': 'right'},
    'MN': {'plugs': 'C, E', 'side': 'right'}, 'ME': {'plugs': 'C, F', 'side': 'right'},
    'MS': {'plugs': 'A, B', 'side': 'left'}, 'MA': {'plugs': 'C, E', 'side': 'right'},
    'MZ': {'plugs': 'C, F, M', 'side': 'left'}, 'MM': {'plugs': 'A, C, D, G, I', 'side': 'right'},
    'NA': {'plugs': 'D, M', 'side': 'left'}, 'NR': {'plugs': 'I', 'side': 'left'},
    'NP': {'plugs': 'C, D, M', 'side': 'left'}, 'NL': {'plugs': 'C, F', 'side': 'right'},
    'NC': {'plugs': 'C, E', 'side': 'right'}, 'NZ': {'plugs': 'I', 'side': 'left'},
    'NI': {'plugs': 'A, B', 'side': 'right'}, 'NE': {'plugs': 'A, B, C, D, E, F', 'side': 'right'},
    'NG': {'plugs': 'D, G', 'side': 'left'}, 'NU': {'plugs': 'I', 'side': 'left'},
    'NF': {'plugs': 'I', 'side': 'left'}, 'MK': {'plugs': 'C, F', 'side': 'right'},
    'NO': {'plugs': 'C, F', 'side': 'right'}, 'OM': {'plugs': 'C, G', 'side': 'right'},
    'PK': {'plugs': 'C, D, G, M', 'side': 'left'}, 'PW': {'plugs': 'A, B', 'side': 'right'},
    'PS': {'plugs': 'C, H, M', 'side': 'right'}, 'PA': {'plugs': 'A, B', 'side': 'right'},
    'PG': {'plugs': 'I', 'side': 'left'}, 'PY': {'plugs': 'C', 'side': 'right'},
    'PE': {'plugs': 'A, C', 'side': 'right'}, 'PH': {'plugs': 'A, B, C', 'side': 'right'},
    'PN': {'plugs': 'I', 'side': 'left'}, 'PL': {'plugs': 'C, E', 'side': 'right'},
    'PT': {'plugs': 'C, F', 'side': 'right'}, 'PR': {'plugs': 'A, B', 'side': 'right'},
    'QA': {'plugs': 'G', 'side': 'left'}, 'RE': {'plugs': 'C, E', 'side': 'right'},
    'RO': {'plugs': 'C, F', 'side': 'right'}, 'RU': {'plugs': 'C, F', 'side': 'right'},
    'RW': {'plugs': 'C, E', 'side': 'right'}, 'BL': {'plugs': 'C, E', 'side': 'right'},
    'SH': {'plugs': 'G', 'side': 'left'}, 'KN': {'plugs': 'A, B, D, G', 'side': 'left'},
    'LC': {'plugs': 'G', 'side': 'left'}, 'MF': {'plugs': 'C, E', 'side': 'right'},
    'PM': {'plugs': 'C, E', 'side': 'right'}, 'VC': {'plugs': 'A, C, E, G, I', 'side': 'left'},
    'WS': {'plugs': 'I', 'side': 'left'}, 'SM': {'plugs': 'C, F, L', 'side': 'right'},
    'ST': {'plugs': 'C, F', 'side': 'right'}, 'SA': {'plugs': 'G', 'side': 'right'},
    'SN': {'plugs': 'C, D, E, K', 'side': 'right'}, 'RS': {'plugs': 'C, F', 'side': 'right'},
    'SC': {'plugs': 'G', 'side': 'left'}, 'SL': {'plugs': 'D, G', 'side': 'left'},
    'SG': {'plugs': 'G', 'side': 'left'}, 'SX': {'plugs': 'A, B', 'side': 'right'},
    'SK': {'plugs': 'C, E', 'side': 'right'}, 'SI': {'plugs': 'C, F', 'side': 'right'},
    'SB': {'plugs': 'I', 'side': 'left'}, 'SO': {'plugs': 'C', 'side': 'right'},
    'ZA': {'plugs': 'C, M, N', 'side': 'left'}, 'GS': {'plugs': 'G', 'side': 'left'},
    'SS': {'plugs': 'C, D', 'side': 'right'}, 'ES': {'plugs': 'C, F', 'side': 'right'},
    'LK': {'plugs': 'D, G, M', 'side': 'left'}, 'SD': {'plugs': 'C, D', 'side': 'right'},
    'SR': {'plugs': 'C, F', 'side': 'left'}, 'SJ': {'plugs': 'C, F', 'side': 'right'},
    'SZ': {'plugs': 'M', 'side': 'left'}, 'SE': {'plugs': 'C, F', 'side': 'right'},
    'CH': {'plugs': 'C, J', 'side': 'right'}, 'SY': {'plugs': 'C, E, L', 'side': 'right'},
    'TW': {'plugs': 'A, B', 'side': 'right'}, 'TJ': {'plugs': 'C, F', 'side': 'right'},
    'TZ': {'plugs': 'D, G', 'side': 'left'}, 'TH': {'plugs': 'A, B, C, O', 'side': 'left'},
    'TL': {'plugs': 'C, E, F, I', 'side': 'right'}, 'TG': {'plugs': 'C', 'side': 'right'},
    'TK': {'plugs': 'I', 'side': 'left'}, 'TO': {'plugs': 'I', 'side': 'left'},
    'TT': {'plugs': 'A, B', 'side': 'left'}, 'TN': {'plugs': 'C, E', 'side': 'right'},
    'TR': {'plugs': 'C, F', 'side': 'right'}, 'TM': {'plugs': 'C, F', 'side': 'right'},
    'TC': {'plugs': 'A, B', 'side': 'left'}, 'TV': {'plugs': 'I', 'side': 'left'},
    'UG': {'plugs': 'G', 'side': 'left'}, 'UA': {'plugs': 'C, F', 'side': 'right'},
    'AE': {'plugs': 'G', 'side': 'right'}, 'GB': {'plugs': 'G', 'side': 'left'},
    'US': {'plugs': 'A, B', 'side': 'right'}, 'UY': {'plugs': 'C, F, L', 'side': 'right'},
    'UZ': {'plugs': 'C, F', 'side': 'right'}, 'VU': {'plugs': 'I', 'side': 'left'},
    'VA': {'plugs': 'C, F, L', 'side': 'right'}, 'VE': {'plugs': 'A, B', 'side': 'right'},
    'VN': {'plugs': 'A, C, G', 'side': 'right'}, 'VG': {'plugs': 'A, B', 'side': 'left'},
    'VI': {'plugs': 'A, B', 'side': 'right'}, 'WF': {'plugs': 'C, E', 'side': 'right'},
    'EH': {'plugs': 'C, E', 'side': 'right'}, 'YE': {'plugs': 'A, C, G', 'side': 'right'},
    'ZM': {'plugs': 'C, D, G', 'side': 'left'}, 'ZW': {'plugs': 'D, G', 'side': 'left'}
}

# EU and EEA countries for Roam Like at Home
RLAH_COUNTRIES = [
    'AT', 'BE', 'BG', 'HR', 'CY', 'CZ', 'DK', 'EE', 'FI', 'FR', 'DE', 'GR', 'HU', 'IE', 'IT', 
    'LV', 'LT', 'LU', 'MT', 'NL', 'PL', 'PT', 'RO', 'SK', 'SI', 'ES', 'SE', # EU
    'IS', 'LI', 'NO' # EEA
]

def sync_static_data(db: Session):
    """Update practical info using defaults and legacy data"""
    synced = 0
    countries = db.query(models.Country).all()
    
    for country in countries:
        iso2 = country.iso_alpha2.upper()
        # Merge legacy tech data with overrides
        tech = LEGACY_TECH_DATA.get(iso2, {})
        overrides = TECH_DATA.get(iso2, {})
        tech.update(overrides)
        
        region = REGIONAL_DEFAULTS.get(country.continent, REGIONAL_DEFAULTS['Europe'])
        
        # Determine values
        vlt = tech.get('voltage', region['voltage'])
        frq = tech.get('freq', region['freq'])
        hrs = tech.get('hours', region['hours'])
        esim = region['esim']
        net = region['internet']
        
        # Payment/Safety Logic
        water_safe = iso2 in RLAH_COUNTRIES or iso2 in ['US', 'CA', 'AU', 'NZ', 'JP', 'CH']
        water_brushing = water_safe or country.continent in ['Europe', 'Americas']
        card_acc = "Wysoka" if iso2 in RLAH_COUNTRIES or iso2 in ['US', 'CA', 'AU', 'NZ', 'JP', 'CH'] else "Średnia"
        
        practical = db.query(models.PracticalInfo).filter(models.PracticalInfo.country_id == country.id).first()
        if not practical:
            practical = models.PracticalInfo(country_id=country.id)
            db.add(practical)
            
        practical.plug_types = tech.get('plugs', 'C')
        practical.driving_side = tech.get('side', 'right')
        practical.voltage = vlt
        practical.frequency = frq
        practical.store_hours = hrs
        practical.esim_available = esim
        practical.internet_notes = net
        practical.tap_water_safe = water_safe
        practical.water_safe_for_brushing = water_brushing
        practical.card_acceptance = card_acc
        practical.last_updated = func.now()
        synced += 1
        
    db.commit()
    logger.info(f"Synced practical data for {synced} countries")
    return {"synced": synced}
