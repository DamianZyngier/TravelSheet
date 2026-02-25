import httpx
from sqlalchemy.orm import Session
from .. import models
from datetime import date
import asyncio
import logging
from .utils import translate_to_pl, get_headers

logger = logging.getLogger("uvicorn")

async def sync_all_holidays(db: Session):
    """Sync holidays for all countries using Nager.Date API"""
    countries = db.query(models.Country).all()
    logger.info(f"Syncing holidays for {len(countries)} countries...")
    results = {"synced": 0, "errors": 0}
    
    for i, country in enumerate(countries):
        try:
            if (i+1) % 20 == 0:
                logger.info(f"[{i+1}/{len(countries)}] Syncing {country.iso_alpha2} holidays...")
            res = await sync_holidays(db, country.iso_alpha2)
            if "error" in res:
                results["errors"] += 1
                logger.error(f"  - Error for {country.iso_alpha2}: {res['error']}")
            else:
                results["synced"] += 1
            
            await asyncio.sleep(0.2)
        except Exception as e:
            logger.error(f"Failed to sync holidays for {country.iso_alpha2}: {str(e)}")
            results["errors"] += 1
            
    logger.info(f"Holiday sync completed: {results['synced']} success, {results['errors']} errors.")
    return results

async def sync_holidays(db: Session, iso2: str):
    """Sync holidays for a country from Nager.Date API with automatic translation"""
    current_year = date.today().year
    
    # Nager.Date API
    url = f"https://date.nager.at/api/v3/PublicHolidays/{current_year}/{iso2.upper()}"

    async with httpx.AsyncClient(timeout=15.0) as client:
        try:
            response = await client.get(url, headers=get_headers())
            if response.status_code != 200:
                return {"error": f"API returned {response.status_code} for {iso2}"}
            holidays_data = response.json()
        except Exception as e:
            return {"error": f"Failed to fetch holidays for {iso2}: {str(e)}"}

    country = db.query(models.Country).filter(models.Country.iso_alpha2 == iso2.upper()).first()
    if not country:
        return {"error": "Country not found"}

    # Clear existing holidays for current year
    db.query(models.Holiday).filter(
        models.Holiday.country_id == country.id,
        models.Holiday.date >= date(current_year, 1, 1),
        models.Holiday.date <= date(current_year, 12, 31)
    ).delete()

    synced = 0
    for h in holidays_data:
        try:
            original_name = h.get('name') or h.get('localName')
            name_pl = translate_to_pl(original_name)
            
            holiday = models.Holiday(
                country_id=country.id,
                name=name_pl,
                name_local=h.get('localName'),
                date=date.fromisoformat(h.get('date')),
                type='Public'
            )
            db.add(holiday)
            synced += 1
        except Exception as e:
            logger.error(f"Error saving holiday {h}: {e}")
            continue

    db.commit()
    return {"status": "success", "synced": synced}
