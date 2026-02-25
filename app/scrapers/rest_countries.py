import httpx
from sqlalchemy.orm import Session
from .. import models
import logging
import asyncio
from .utils import translate_to_pl, get_headers

logger = logging.getLogger("uvicorn")

async def sync_countries(db: Session):
    """
    Syncs base country list from REST Countries API.
    Uses fields filter to reduce data size and avoid 400 errors.
    """
    # Optimized URL with fields to avoid 400 errors
    fields = "name,cca2,cca3,capital,flags,population,region,continents,latlng,translations,languages,currencies"
    url = f"https://restcountries.com/v3.1/all?fields={fields}"
    
    logger.info(f"Fetching countries from {url}...")
    
    data = None
    async with httpx.AsyncClient(timeout=40.0, follow_redirects=True) as client:
        for attempt in range(3):
            try:
                resp = await client.get(url, headers=get_headers())
                if resp.status_code == 200:
                    data = resp.json()
                    break
                else:
                    logger.error(f"Attempt {attempt+1}: REST Countries returned {resp.status_code}")
                    logger.error(f"Response: {resp.text[:200]}")
                    if attempt < 2: await asyncio.sleep(2)
            except Exception as e:
                logger.error(f"Attempt {attempt+1} failed: {e}")
                if attempt < 2: await asyncio.sleep(2)

    if not data:
        # Fallback to absolute minimum if API fails but we need a list
        logger.error("All attempts to fetch from REST Countries failed.")
        return {"error": "Failed to fetch REST Countries after 3 attempts"}

    logger.info(f"Successfully fetched {len(data)} countries from API.")

    results = {"synced": 0, "updated": 0}
    
    for i, country_data in enumerate(data):
        iso2 = country_data.get("cca2")
        if not iso2: continue
        
        if (i+1) % 50 == 0:
            logger.info(f"Processing country {i+1}/{len(data)}: {iso2}")

        country = db.query(models.Country).filter(models.Country.iso_alpha2 == iso2).first()
        
        # Build basic data
        name_en = country_data.get("name", {}).get("common")
        name_pl = country_data.get("translations", {}).get("pol", {}).get("common") or name_en
        
        capital_list = country_data.get("capital", [])
        capital = capital_list[0] if capital_list else None
        
        # Flag and other details
        flag_url = country_data.get("flags", {}).get("png") or country_data.get("flags", {}).get("svg")
        population = country_data.get("population")
        region = country_data.get("region")
        
        continents = country_data.get("continents", [])
        continent = continents[0] if continents else None
        
        coords = country_data.get("latlng", [None, None])
        # Sometimes it returns empty list
        lat = coords[0] if len(coords) > 0 else None
        lon = coords[1] if len(coords) > 1 else None

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
                population=population,
                latitude=lat,
                longitude=lon
            )
            db.add(country)
            db.flush()
            results["synced"] += 1
        else:
            # Update existing basic info
            country.population = population
            country.flag_url = flag_url
            country.latitude = lat
            country.longitude = lon
            results["updated"] += 1

        # Languages (Translate)
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

        # Currencies (Translate name)
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

    db.commit()
    logger.info(f"REST Countries sync completed: {results['synced']} new, {results['updated']} updated.")
    return results
