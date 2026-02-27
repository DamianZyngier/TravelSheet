import httpx
from sqlalchemy.orm import Session
from .. import models
import logging
import asyncio
from .utils import translate_to_pl, get_headers, normalize_polish_text

logger = logging.getLogger("uvicorn")

async def fetch_data(url):
    async with httpx.AsyncClient(timeout=40.0, follow_redirects=True) as client:
        for attempt in range(3):
            try:
                resp = await client.get(url, headers=get_headers())
                if resp.status_code == 200:
                    return resp.json()
                else:
                    logger.error(f"Attempt {attempt+1}: REST Countries returned {resp.status_code}")
                    if attempt < 2: await asyncio.sleep(2)
            except Exception as e:
                logger.error(f"Attempt {attempt+1} failed: {e}")
                if attempt < 2: await asyncio.sleep(2)
    return None

def normalize_polish_name(name: str, iso2: str = None) -> str:
    """Fix common errors in Polish country names from external APIs."""
    if iso2 == 'SS' and name == 'Sudan':
        return 'Sudan Południowy'
    return normalize_polish_text(name)

async def sync_countries(db: Session):
    """
    Syncs base country list from REST Countries API.
    Handles the 10-field limit by making multiple requests.
    """
    # Request 1: Basic info
    fields1 = "name,cca2,cca3,capital,region,continents,latlng,translations,languages,currencies"
    url1 = f"https://restcountries.com/v3.1/all?fields={fields1}"
    
    # Request 2: Extra info (population, area, idd)
    fields2 = "cca2,population,area,idd"
    url2 = f"https://restcountries.com/v3.1/all?fields={fields2}"
    
    logger.info("Fetching country data from REST Countries (Part 1)...")
    data1 = await fetch_data(url1)
    
    logger.info("Fetching country data from REST Countries (Part 2)...")
    data2 = await fetch_data(url2)

    if not data1:
        return {"error": "Failed to fetch primary country data"}

    # Merge data by ISO2
    extra_info = {item.get("cca2"): item for item in data2} if data2 else {}

    results = {"synced": 0, "updated": 0, "skipped": 0, "errors": []}
    
    for i, country_data in enumerate(data1):
        try:
            iso2 = country_data.get("cca2")
            if not iso2:
                results["skipped"] += 1
                continue
            
            extra = extra_info.get(iso2, {})
            
            if (i+1) % 50 == 0:
                logger.info(f"Processing country {i+1}/{len(data1)}: {iso2}")

            country = db.query(models.Country).filter(models.Country.iso_alpha2 == iso2).first()
            
            # Build basic data
            name_en = country_data.get("name", {}).get("common")
            name_pl = country_data.get("translations", {}).get("pol", {}).get("common") or name_en
            name_pl = normalize_polish_name(name_pl, iso2)
            
            capital_list = country_data.get("capital", [])
            capital = capital_list[0] if capital_list else None
            
            # Flag URL
            flag_url = f"https://flagcdn.com/w320/{iso2.lower()}.png"
            region = country_data.get("region")
            continents = country_data.get("continents", [])
            continent = continents[0] if continents else None
            
            coords = country_data.get("latlng", [])
            lat = coords[0] if len(coords) > 0 else None
            lon = coords[1] if len(coords) > 1 else None

            # Population, Area & Phone Code
            population = extra.get("population")
            area = extra.get("area")
            idd = extra.get("idd", {})
            root = idd.get("root", "")
            suffixes = idd.get("suffixes", [])
            phone_code = f"{root}{suffixes[0]}" if root and suffixes else (root if root else None)

            if not country:
                country = models.Country(
                    iso_alpha2=iso2,
                    iso_alpha3=country_data.get("cca3"),
                    name=name_en,
                    name_pl=name_pl,
                    capital=capital,
                    continent=continent,
                    region=region,
                    flag_url=flag_url,
                    latitude=lat,
                    longitude=lon,
                    population=population,
                    area=area,
                    phone_code=phone_code
                )
                db.add(country)
                db.flush()
                results["synced"] += 1
            else:
                country.name_pl = name_pl # Ensure name is updated if fixed
                country.flag_url = flag_url
                country.latitude = lat
                country.longitude = lon
                country.population = population
                country.area = area
                country.phone_code = phone_code
                results["updated"] += 1

            # Languages
            langs = country_data.get("languages", {})
            if langs:
                db.query(models.Language).filter(models.Language.country_id == country.id).delete()
                for code, name in langs.items():
                    db.add(models.Language(
                        country_id=country.id,
                        name=translate_to_pl(name),
                        code=code,
                        is_official=True
                    ))

            # Currencies
            currencies = country_data.get("currencies", {})
            if currencies:
                db.query(models.Currency).filter(models.Currency.country_id == country.id).delete()
                for code, info in currencies.items():
                    db.add(models.Currency(
                        country_id=country.id,
                        code=code,
                        name=translate_to_pl(info.get("name")),
                        symbol=info.get("symbol")
                    ))
        except Exception as e:
            err_msg = f"Error processing country {country_data.get('cca2', 'unknown')}: {str(e)}"
            logger.error(err_msg)
            results["errors"].append(err_msg)

    db.commit()
    logger.info(f"REST Countries sync completed: {results['synced']} new, {results['updated']} updated, {len(results['errors'])} errors.")
    return results
