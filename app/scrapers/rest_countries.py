import httpx
from sqlalchemy.orm import Session
from .. import models, crud
import logging

logger = logging.getLogger("uvicorn")

async def sync_countries(db: Session):
    """Sync all countries from REST Countries API with full field enforcement"""

    async with httpx.AsyncClient() as client:
        # Request essential fields. 
        fields = "name,cca2,cca3,flag,flags,currencies,languages,capital,region,subregion,population,continents,translations"
        try:
            response = await client.get(f"https://restcountries.com/v3.1/all?fields={fields}", timeout=30.0)
            response.raise_for_status()
            countries_data = response.json()
        except Exception as e:
            logger.error(f"Primary API request failed: {e}")
            # Fallback
            fields = "name,cca2,cca3,flag,flags,currencies,translations,continents,region"
            response = await client.get(f"https://restcountries.com/v3.1/all?fields={fields}")
            countries_data = response.json()

    synced = 0
    errors = []

    if not isinstance(countries_data, list):
        return {"synced": 0, "error": "API did not return a list"}

    for data in countries_data:
        iso2 = data.get('cca2', '??')
        try:
            iso3 = data.get('cca3')
            name_pl = data.get('translations', {}).get('pol', {}).get('common')
            if not name_pl:
                name_pl = data.get('name', {}).get('common')

            # Get continent (API returns a list, e.g. ["Europe"])
            continents = data.get('continents', [])
            continent = continents[0] if continents else data.get('region')

            country_dict = {
                'iso_alpha2': iso2,
                'iso_alpha3': iso3,
                'name': data.get('name', {}).get('common'),
                'name_pl': name_pl,
                'name_local': list(data.get('name', {}).get('nativeName', {}).values())[0].get('common') if data.get('name', {}).get('nativeName') else None,
                'capital': data.get('capital', [None])[0] if data.get('capital') else None,
                'continent': continent,
                'region': data.get('region'),
                'flag_emoji': data.get('flag'),
                'flag_url': data.get('flags', {}).get('png'),
                'population': data.get('population')
            }

            existing = db.query(models.Country).filter(models.Country.iso_alpha2 == iso2).first()

            if existing:
                # Force update all fields
                for key, value in country_dict.items():
                    setattr(existing, key, value)
                country = existing
            else:
                country = models.Country(**country_dict)
                db.add(country)
                db.flush() # Get ID for relationships

            # Sync languages
            languages = data.get('languages', {})
            db.query(models.Language).filter(models.Language.country_id == country.id).delete()
            for code, name in languages.items():
                lang = models.Language(country_id=country.id, name=name, code=code, is_official=True)
                db.add(lang)

            # Sync currency
            currencies = data.get('currencies', {})
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

    return {"synced": synced, "total": len(countries_data), "errors": errors}
