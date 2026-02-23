import httpx
from sqlalchemy.orm import Session
from .. import models, crud
import logging
from .capitals_pl import CAPITAL_MAPPING_PL

logger = logging.getLogger("uvicorn")

async def sync_countries(db: Session):
    """Sync all countries from REST Countries API with full field enforcement"""

    async with httpx.AsyncClient() as client:
        # Request 1: Essential IDs, Names, and Translations
        try:
            url1 = "https://restcountries.com/v3.1/all?fields=cca2,cca3,name,translations,capital,continents,region,latlng"
            resp1 = await client.get(url1, timeout=30.0)
            resp1.raise_for_status()
            base_data = resp1.json()
            
            # Request 2: Flags, Currencies, Languages, Population
            url2 = "https://restcountries.com/v3.1/all?fields=cca2,flag,flags,currencies,languages,population"
            resp2 = await client.get(url2, timeout=30.0)
            resp2.raise_for_status()
            extra_data = {item['cca2']: item for item in resp2.json()}
        except Exception as e:
            logger.error(f"API request failed: {e}")
            return {"synced": 0, "error": f"API failure: {str(e)}"}

    synced = 0
    errors = []

    for data in base_data:
        iso2 = data.get('cca2')
        if not iso2: continue
        
        try:
            extra = extra_data.get(iso2, {})
            name_pl = data.get('translations', {}).get('pol', {}).get('common') or data.get('name', {}).get('common')

            # Get continent
            continents = data.get('continents', [])
            continent = continents[0] if continents else data.get('region')

            # LatLng
            latlng = data.get('latlng', [None, None])
            lat = latlng[0] if len(latlng) > 0 else None
            lng = latlng[1] if len(latlng) > 1 else None

            country_dict = {
                'iso_alpha2': iso2,
                'iso_alpha3': data.get('cca3'),
                'name': data.get('name', {}).get('common'),
                'name_pl': name_pl,
                'name_local': list(data.get('name', {}).get('nativeName', {}).values())[0].get('common') if data.get('name', {}).get('nativeName') else None,
                'capital': data.get('capital', [None])[0] if data.get('capital') else None,
                'capital_pl': CAPITAL_MAPPING_PL.get(iso2.upper()) or (data.get('capital', [None])[0] if data.get('capital') else None),
                'continent': continent,
                'region': data.get('region'),
                'flag_emoji': extra.get('flag'),
                'flag_url': extra.get('flags', {}).get('png'),
                'population': extra.get('population'),
                'latitude': lat,
                'longitude': lng
            }

            existing = db.query(models.Country).filter(models.Country.iso_alpha2 == iso2).first()

            if existing:
                for key, value in country_dict.items():
                    setattr(existing, key, value)
                country = existing
            else:
                country = models.Country(**country_dict)
                db.add(country)
                db.flush()

            # Sync languages
            languages = extra.get('languages', {})
            db.query(models.Language).filter(models.Language.country_id == country.id).delete()
            for code, name in languages.items():
                lang = models.Language(country_id=country.id, name=name, code=code, is_official=True)
                db.add(lang)

            # Sync currency
            currencies = extra.get('currencies', {})
            if currencies:
                curr_code = list(currencies.keys())[0]
                curr_data = currencies[curr_code]
                existing_curr = db.query(models.Currency).filter(models.Currency.country_id == country.id).first()
                if existing_curr:
                    existing_curr.code = curr_code
                    existing_curr.name = curr_data.get('name')
                    existing_curr.symbol = curr_data.get('symbol')
                else:
                    currency = models.Currency(country_id=country.id, code=curr_code, name=curr_data.get('name'), symbol=curr_data.get('symbol'))
                    db.add(currency)

            db.commit()
            synced += 1

        except Exception as e:
            db.rollback()
            errors.append(f"{iso2}: {str(e)}")
            continue

    return {"synced": synced, "total": len(base_data), "errors": errors}
