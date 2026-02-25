import httpx
from sqlalchemy.orm import Session
from .. import models
import logging
from .utils import translate_to_pl, get_headers

logger = logging.getLogger("uvicorn")

async def sync_countries(db: Session):
    """
    Syncs base country list from REST Countries API.
    Translates languages and currency names to Polish.
    """
    url = "https://restcountries.com/v3.1/all"
    logger.info(f"Fetching countries from {url}...")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            resp = await client.get(url, headers=get_headers())
            resp.raise_for_status()
            data = resp.json()
            logger.info(f"Successfully fetched {len(data)} countries from API.")
        except Exception as e:
            logger.error(f"Failed to fetch REST Countries: {e}")
            return {"error": f"Failed to fetch REST Countries: {e}"}

    results = {"synced": 0, "updated": 0}
    
    for i, country_data in enumerate(data):
        iso2 = country_data.get("cca2")
        if not iso2: continue
        
        if i % 50 == 0:
            logger.info(f"Processing country {i}/{len(data)}: {iso2}")

        country = db.query(models.Country).filter(models.Country.iso_alpha2 == iso2).first()
        
        # Build basic data
        name_en = country_data.get("name", {}).get("common")
        name_pl = country_data.get("translations", {}).get("pol", {}).get("common") or name_en
        capital = country_data.get("capital", [None])[0]
        
        # Flag and other details
        flag_url = country_data.get("flags", {}).get("png")
        population = country_data.get("population")
        region = country_data.get("region")
        continent = country_data.get("continents", [None])[0]
        
        coords = country_data.get("latlng", [None, None])
        lat, lon = coords[0], coords[1]

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
        db.query(models.Currency).filter(models.Currency.country_id == country.id).delete()
        for code, info in currencies.items():
            db.add(models.Currency(
                country_id=country.id,
                code=code,
                name=translate_to_pl(info.get("name")),
                symbol=info.get("symbol")
            ))

    db.commit()
    return results
