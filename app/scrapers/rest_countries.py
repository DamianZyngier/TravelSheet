import httpx
from sqlalchemy.orm import Session
from .. import models
import logging
import asyncio
from sqlalchemy.sql import func
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
                    logger.error(f"Attempt {attempt+1}: ApiCountries returned {resp.status_code}")
                    if attempt < 2: await asyncio.sleep(2)
            except Exception as e:
                logger.error(f"Attempt {attempt+1} failed: {e}")
                if attempt < 2: await asyncio.sleep(2)
    return None

def normalize_polish_name(name: str, iso2: str = None) -> str:
    """Fix common errors in Polish country names from external APIs."""
    if iso2 == 'SS' and name == 'Sudan':
        return 'Sudan Południowy'
    if iso2 == 'GB':
        return 'Wielka Brytania'
    return normalize_polish_text(name)

async def sync_countries(db: Session):
    """
    Syncs base country list from ApiCountries API (drop-in replacement for Rest Countries).
    """
    url = "https://www.apicountries.com/countries"
    
    logger.info("Fetching country data from ApiCountries...")
    data = await fetch_data(url)

    if not data:
        return {"error": "Failed to fetch country data"}

    results = {"synced": 0, "updated": 0, "skipped": 0, "errors": []}
    
    # Manual parent mapping
    MANUAL_PARENTS = {
        'MQ': 'FR', 'RE': 'FR', 'GF': 'FR', 'GP': 'FR', 'YT': 'FR', 'MF': 'FR', 'BL': 'FR', 'PM': 'FR', 'WF': 'FR', 'PF': 'FR', 'NC': 'FR', 'TF': 'FR',
        'AW': 'NL', 'CW': 'NL', 'SX': 'NL', 'BQ': 'NL',
        'PR': 'US', 'GU': 'US', 'AS': 'US', 'VI': 'US', 'MP': 'US', 'UM': 'US',
        'GI': 'GB', 'FK': 'GB', 'BM': 'GB', 'VG': 'GB', 'KY': 'GB', 'MS': 'GB', 'TC': 'GB', 'SH': 'GB', 'PN': 'GB', 'GS': 'GB', 'IO': 'GB', 'GG': 'GB', 'JE': 'GB', 'IM': 'GB', 'AI': 'GB',
        'AX': 'FI', 'GL': 'DK', 'FO': 'DK',
        'SJ': 'NO', 'BV': 'NO', 'CC': 'AU', 'CX': 'AU', 'NF': 'AU', 'HM': 'AU',
        'TK': 'NZ', 'CK': 'NZ', 'NU': 'NZ',
        'MO': 'CN', 'HK': 'CN',
        'EH': 'MA'
    }
    
    for i, country_data in enumerate(data):
        iso2 = country_data.get("alpha2Code")
        if not iso2:
            continue
            
        try:
            if (i+1) % 50 == 0:
                logger.info(f"Processing country {i+1}/{len(data)}: {iso2}")

            country = db.query(models.Country).filter(models.Country.iso_alpha2 == iso2).first()
            
            # Build basic data
            name_en = country_data.get("name")
            # Fallback for Polish name: check translations (unlikely in ApiCountries for 'pol'), 
            # otherwise use translate_to_pl on name_en.
            name_pl = country_data.get("translations", {}).get("pol") or country_data.get("translations", {}).get("pl")
            if not name_pl:
                name_pl = translate_to_pl(name_en)
            
            name_pl = normalize_polish_name(name_pl, iso2)
            
            capital = country_data.get("capital")
            
            flag_url = f"https://flagcdn.com/w320/{iso2.lower()}.png"
            region = country_data.get("region") # In ApiCountries this is the continent (Asia, Europe, etc.)
            subregion = country_data.get("subregion")
            
            coords = country_data.get("latlng", [])
            lat = coords[0] if len(coords) > 0 else None
            lon = coords[1] if len(coords) > 1 else None

            population = country_data.get("population")
            area = country_data.get("area")
            
            # Phone code from callingCodes
            calling_codes = country_data.get("callingCodes", [])
            phone_code = f"+{calling_codes[0]}" if calling_codes else None
            
            is_independent = country_data.get("independent", True)

            if not country:
                country = models.Country(
                    iso_alpha2=iso2,
                    iso_alpha3=country_data.get("alpha3Code"),
                    name=name_en,
                    name_pl=name_pl,
                    capital=capital,
                    continent=region,
                    region=subregion,
                    flag_url=flag_url,
                    latitude=lat,
                    longitude=lon,
                    population=population,
                    area=area,
                    phone_code=phone_code,
                    is_independent=is_independent
                )
                db.add(country)
                db.flush()
                results["synced"] += 1
            else:
                country.name_pl = name_pl 
                country.flag_url = flag_url
                country.latitude = lat
                country.longitude = lon
                country.population = population
                country.area = area
                country.phone_code = phone_code
                country.is_independent = is_independent
                # Trigger country.updated_at
                country.updated_at = func.now()
                results["updated"] += 1

            # Languages
            langs = country_data.get("languages", [])
            if langs:
                db.query(models.Language).filter(models.Language.country_id == country.id).delete()
                for lang_info in langs:
                    l_name = lang_info.get("name")
                    l_code = lang_info.get("iso639_1") or lang_info.get("iso639_2")
                    if l_name:
                        db.add(models.Language(
                            country_id=country.id,
                            name=translate_to_pl(l_name),
                            code=l_code,
                            is_official=True,
                            last_updated=func.now()
                        ))

            # Currencies
            currencies = country_data.get("currencies", [])
            if currencies:
                db.query(models.Currency).filter(models.Currency.country_id == country.id).delete()
                # Use the first currency
                curr = currencies[0]
                db.add(models.Currency(
                    country_id=country.id,
                    code=curr.get("code"),
                    name=translate_to_pl(curr.get("name")),
                    symbol=curr.get("symbol"),
                    last_updated=func.now()
                ))
        except Exception as e:
            err_msg = f"Error processing country {iso2}: {str(e)}"
            logger.error(err_msg)
            results["errors"].append(err_msg)

    db.commit()
    
    # Second pass for parent mapping
    logger.info("Updating parent/territory relationships...")
    for iso2, parent_iso in MANUAL_PARENTS.items():
        country = db.query(models.Country).filter(models.Country.iso_alpha2 == iso2).first()
        parent = db.query(models.Country).filter(models.Country.iso_alpha2 == parent_iso).first()
        if country and parent:
            country.parent_id = parent.id
    
    db.commit()
    
    logger.info(f"ApiCountries sync completed: {results['synced']} new, {results['updated']} updated, {len(results['errors'])} errors.")
    return results
