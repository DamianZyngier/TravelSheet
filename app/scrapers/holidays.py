import httpx
from sqlalchemy.orm import Session
from .. import models
from datetime import date
import asyncio
import logging
from .utils import translate_to_pl, get_headers

logger = logging.getLogger("uvicorn")

async def sync_holidays(db: Session, iso2: str, client: httpx.AsyncClient):
    """Sync holidays for a country from Nager.Date API with automatic translation"""
    current_year = date.today().year
    url = f"https://date.nager.at/api/v3/PublicHolidays/{current_year}/{iso2.upper()}"

    try:
        response = await client.get(url, headers=get_headers())
        if response.status_code != 200:
            return {"error": f"HTTP {response.status_code}"}
        holidays_data = response.json()
    except Exception as e:
        return {"error": str(e)}

    country = db.query(models.Country).filter(models.Country.iso_alpha2 == iso2.upper()).first()
    if not country: return {"error": "Country not found"}

    db.query(models.Holiday).filter(
        models.Holiday.country_id == country.id,
        models.Holiday.date >= date(current_year, 1, 1),
        models.Holiday.date <= date(current_year, 12, 31)
    ).delete()

    for h in holidays_data:
        try:
            original_name = h.get('name') or h.get('localName')
            name_pl = translate_to_pl(original_name)
            
            db.add(models.Holiday(
                country_id=country.id,
                name=name_pl,
                name_local=h.get('localName'),
                date=date.fromisoformat(h.get('date')),
                type='Public'
            ))
        except: continue

    db.commit()
    return {"status": "success"}

async def sync_all_holidays(db: Session):
    countries = db.query(models.Country).all()
    results = {"synced": 0, "errors": 0}
    
    semaphore = asyncio.Semaphore(20)
    
    async def limited_sync(country, client):
        async with semaphore:
            res = await sync_holidays(db, country.iso_alpha2, client)
            if "status" in res:
                results["synced"] += 1
            else:
                results["errors"] += 1

    logger.info(f"Starting parallel Holiday sync for {len(countries)} countries...")
    async with httpx.AsyncClient(timeout=20.0, follow_redirects=True) as client:
        await asyncio.gather(*(limited_sync(c, client) for c in countries))
            
    return results
