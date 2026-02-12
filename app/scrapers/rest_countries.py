import httpx
from sqlalchemy.orm import Session
from .. import models, crud

async def sync_countries(db: Session):
    """Sync all countries from REST Countries API"""

    async with httpx.AsyncClient() as client:
        response = await client.get("https://restcountries.com/v3.1/all")
        countries_data = response.json()

    synced = 0
    errors = []

    for data in countries_data:
        try:
            iso2 = data.get('cca2')
            iso3 = data.get('cca3')

            # Check if exists
            existing = crud.get_country_by_iso2(db, iso2)

            country_dict = {
                'iso_alpha2': iso2,
                'iso_alpha3': iso3,
                'name': data.get('name', {}).get('common'),
                'name_local': list(data.get('name', {}).get('nativeName', {}).values())[0].get('common') if data.get('name', {}).get('nativeName') else None,
                'capital': data.get('capital', [None])[0],
                'continent': data.get('continents', [None])[0],
                'region': data.get('region'),
                'flag_emoji': data.get('flag'),
                'flag_url': data.get('flags', {}).get('png'),
                'population': data.get('population')
            }

            if existing:
                # Update
                for key, value in country_dict.items():
                    setattr(existing, key, value)
            else:
                # Create
                country = crud.create_country(db, country_dict)

                # Add languages
                languages = data.get('languages', {})
                for code, name in languages.items():
                    lang = models.Language(
                        country_id=country.id,
                        name=name,
                        code=code,
                        is_official=True
                    )
                    db.add(lang)

                # Add currency
                currencies = data.get('currencies', {})
                if currencies:
                    curr_code = list(currencies.keys())[0]
                    curr_data = currencies[curr_code]

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
