from sqlalchemy.orm import Session
from sqlalchemy import func
from .. import models
import logging
import re

logger = logging.getLogger("uvicorn")

# Robust mapping of transport apps by country
# Format: {ISO2: "App1, App2 (cities), ..."}
TRANSPORT_MAPPING = {
    'PL': 'Uber, Bolt, Free Now (największe miasta)',
    'DE': 'Uber, Free Now, Bolt (Berlin, Monachium, Hamburg, Frankfurt)',
    'FR': 'Uber, Bolt, Free Now (Paryż, Lyon, Nicea)',
    'ES': 'Uber, Cabify, Free Now, Bolt (Madryt, Barcelona, Walencja, Sewilla)',
    'IT': 'Free Now, IT Taxi, Uber (głównie Uber Black w Rzymie i Mediolanie)',
    'GB': 'Uber, Bolt, Free Now (Londyn, Manchester, Birmingham)',
    'PT': 'Uber, Bolt, Free Now (Lizbona, Porto, Faro)',
    'GR': 'Uber (Ateny, Santorini, Mykonos), Free Now (Ateny, Saloniki)',
    'TR': 'BiTaksi (cała Turcja), Uber (Stambuł, Ankara)',
    'CZ': 'Uber, Bolt (Praga, Brno, Ostrawa)',
    'HU': 'Bolt (Budapeszt - jedyna oficjalna aplikacja typu ride-hailing)',
    'AT': 'Uber, Bolt, Free Now (Wiedeń, Salzburg)',
    'HR': 'Uber, Bolt (Zagrzeb, Split, Dubrownik, Zadar)',
    'TH': 'Grab (cały kraj), Bolt (Bangkok, Phuket, Chiang Mai)',
    'VN': 'Grab, Gojek, Be (Hanoi, Ho Chi Minh City, Da Nang)',
    'ID': 'Gojek, Grab (Dżakarta, Bali, Surabaya)',
    'SG': 'Grab, Gojek, Tada, Ryde',
    'MY': 'Grab (cały kraj), AirAsia Ride',
    'PH': 'Grab, JoyRide (Manila, Cebu)',
    'AE': 'Careem (najpopularniejsza), Uber (Dubaj, Abu Zabi)',
    'SA': 'Careem, Uber, Kaiian (Rijad, Dżudda)',
    'EG': 'Uber, Careem, InDrive (Kair, Aleksandria)',
    'MA': 'Uber (czasowo zawieszony), InDrive, Careem (Casablanca, Marrakesz)',
    'US': 'Uber, Lyft (cały kraj)',
    'CA': 'Uber, Lyft (Toronto, Vancouver, Montreal)',
    'MX': 'Uber, Didi, Cabify (Meksyk, Cancun, Guadalajara)',
    'BR': 'Uber, 99 (Didi), Cabify (Sao Paulo, Rio de Janeiro)',
    'AR': 'Uber, Cabify (Buenos Aires, Mendoza)',
    'AU': 'Uber, Ola, DiDi (Sydney, Melbourne, Brisbane)',
    'NZ': 'Uber, Ola (Auckland, Wellington, Christchurch)',
    'ZA': 'Uber, Bolt (Johannesburg, Kapsztad, Durban)',
    'KE': 'Uber, Bolt, Little (Nairobi, Mombasa)',
    'IL': 'Gett (najpopularniejsza), Uber, Yango',
    'UA': 'Uber, Bolt, Uklon (Kijów, Lwów, Odessa)',
    'RO': 'Uber, Bolt, Free Now (Bukareszt, Kluż-Napoka)',
    'BG': 'TaxiMe, Yellow! (Sofia - brak Ubera/Bolta)',
    'IE': 'Uber (tylko licencjonowane taksówki), Free Now, Bolt (Dublin)',
    'CH': 'Uber (Zurych, Genewa, Bazylea)',
    'SE': 'Uber, Bolt (Sztokholm, Göteborg)',
    'NO': 'Uber, Bolt (Oslo)',
    'DK': 'Viggo, Dantaxi (Kopenhaga - brak Ubera)',
    'FI': 'Uber, Bolt (Helsinki)',
    'BE': 'Uber, Bolt, Free Now (Bruksela, Antwerpia)',
    'NL': 'Uber, Bolt, Free Now (Amsterdam, Rotterdam, Haga)',
    'IS': 'Hreyfill, BSR (Rejkiawik - brak Ubera/Bolta)',
    'CY': 'Bolt, RideNow (Nikozja, Limassol, Pafos)',
    'MT': 'Bolt, Uber, eCabs (cała wyspa)',
    'GE': 'Bolt, Yandex.Taxi (Tbilisi, Batumi)',
    'AM': 'Yandex.Taxi, GG (Erywań)',
    'AZ': 'Bolt, Uber, Yandex.Taxi (Baku)',
    'KZ': 'Yandex.Taxi, Uber (Ałmaty, Astana)',
    'UZ': 'Yandex.Taxi, MyTaxi (Taszkent, Samarkanda)',
    'JO': 'Uber, Careem (Amman)',
    'QA': 'Uber, Careem, Karwa (Doha)',
    'LK': 'PickMe (najlepsza), Uber (Kolombo, Kandy)',
    'NP': 'Pathao, InDrive (Katmandu)',
    'KH': 'PassApp, Grab (Phnom Penh, Siem Reap)',
    'LA': 'Loca, KokKok Move (Wientian, Luang Prabang)',
    'TW': 'Uber, LINE Taxi (Tajpej, Kaohsiung)',
    'KR': 'Kakao T (najpopularniejsza), Uber (jako UT)',
    'JP': 'Uber (głównie Tokio/Osaka), GO, DiDi, S.RIDE',
}

# Regional fallbacks if not in mapping
REGIONAL_APPS = {
    'Europe': 'Uber, Bolt, Free Now',
    'Asia': 'Grab, Gojek, Uber',
    'Americas': 'Uber, Lyft, Cabify',
    'Africa': 'Uber, Bolt, InDrive',
    'Middle East': 'Careem, Uber',
    'Oceania': 'Uber, Ola, DiDi'
}

async def sync_transport_apps(db: Session):
    """
    Updates popular_apps column with transport-specific data.
    """
    countries = db.query(models.Country).all()
    synced = 0
    
    for country in countries:
        iso2 = country.iso_alpha2.upper()
        
        # 1. Start with manual mapping
        apps = TRANSPORT_MAPPING.get(iso2)
        
        # 2. If not found, look into practical info or wiki summary for clues
        if not apps:
            clues = []
            source_text = ""
            if country.wiki_summary: source_text += country.wiki_summary
            if country.practical and country.practical.internet_notes: source_text += country.practical.internet_notes
            
            for app_name in ["Uber", "Bolt", "Free Now", "Grab", "Careem", "Gojek", "Lyft", "Didi", "Cabify"]:
                if app_name.lower() in source_text.lower():
                    clues.append(app_name)
            
            if clues:
                apps = ", ".join(clues)
            else:
                # 3. Use regional fallback
                apps = REGIONAL_APPS.get(country.continent, "Uber, Bolt")
        
        # Update database
        country.popular_apps = apps
        synced += 1
        
    db.commit()
    logger.info(f"Synced transport apps for {synced} countries")
    return {"success": synced}
