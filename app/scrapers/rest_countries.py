import httpx
from sqlalchemy.orm import Session
from .. import models, crud

async def sync_countries(db: Session):
    """Sync all countries from REST Countries API"""

    async with httpx.AsyncClient() as client:
        # Request exactly 11 fields to include translations
        fields = "name,cca2,cca3,flags,currencies,languages,capital,region,population,continents,translations"
        response = await client.get(f"https://restcountries.com/v3.1/all?fields={fields}")
        countries_data = response.json()
        
        if isinstance(countries_data, dict) and countries_data.get('status') == 400:
            # Fallback - maybe even fewer fields?
            fields = "name,cca2,cca3,flags,currencies,translations"
            response = await client.get(f"https://restcountries.com/v3.1/all?fields={fields}")
            countries_data = response.json()

    synced = 0
    errors = []

    if not isinstance(countries_data, list):
        return {"synced": 0, "error": "API did not return a list"}

    for data in countries_data:
        iso2 = "Unknown"
        try:
            if not isinstance(data, dict):
                continue
            
            iso2 = data.get('cca2')
            iso3 = data.get('cca3')

            # Extract Polish name from translations
            name_pl = data.get('translations', {}).get('pol', {}).get('common')
            if not name_pl:
                name_pl = data.get('name', {}).get('common')

            # Check if exists
            existing = crud.get_country_by_iso2(db, iso2)

            country_dict = {
                'iso_alpha2': iso2,
                'iso_alpha3': iso3,
                'name': data.get('name', {}).get('common'),
                'name_pl': name_pl,
                'name_local': list(data.get('name', {}).get('nativeName', {}).values())[0].get('common') if data.get('name', {}).get('nativeName') else None,
                'capital': data.get('capital', [None])[0] if data.get('capital') else None,
                'continent': data.get('continents', [None])[0] if data.get('continents') else None,
                'region': data.get('region'),
                'flag_emoji': data.get('flag'),
                'flag_url': data.get('flags', {}).get('png'),
                'population': data.get('population')
            }

            if existing:
                # Update
                for key, value in country_dict.items():
                    setattr(existing, key, value)
                country = existing
            else:
                # Create
                country = crud.create_country(db, country_dict)

            # Always sync languages
            languages = data.get('languages', {})
            # Clear existing languages to avoid duplicates on sync
            db.query(models.Language).filter(models.Language.country_id == country.id).delete()
            for code, name in languages.items():
                lang = models.Language(
                    country_id=country.id,
                    name=name,
                    code=code,
                    is_official=True
                )
                db.add(lang)

            # Always sync currency
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
                    currency = models.Currency(
                        country_id=country.id,
                        code=curr_code,
                        name=curr_data.get('name'),
                        symbol=curr_data.get('symbol')
                    )
                    db.add(currency)

            db.commit()
            synced += 1

        except Exception as e:
            errors.append(f"{iso2}: {str(e)}")
            continue

    return {
        "synced": synced,
        "total": len(countries_data),
        "errors": errors
    }
