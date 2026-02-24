import httpx
from sqlalchemy.orm import Session
from .. import models
from datetime import date
import asyncio
import logging
from deep_translator import GoogleTranslator

logger = logging.getLogger("uvicorn")

# In-memory cache for translations to avoid redundant API calls
translation_cache = {}

def translate_to_pl(text: str) -> str:
    if not text: return text
    if text in translation_cache:
        return translation_cache[text]
    
    try:
        translated = GoogleTranslator(source='auto', target='pl').translate(text)
        translation_cache[text] = translated
        return translated
    except Exception as e:
        logger.error(f"Translation error for '{text}': {e}")
        return text

async def sync_all_holidays(db: Session):
    """Sync holidays for all countries using Nager.Date API"""
    countries = db.query(models.Country).all()
    results = {"synced": 0, "errors": 0}
    
    for country in countries:
        try:
            res = await sync_holidays(db, country.iso_alpha2)
            if "error" in res:
                results["errors"] += 1
            else:
                results["synced"] += 1
            
            # Nager.Date is free, but let's be polite
            await asyncio.sleep(0.2)
        except Exception as e:
            logger.error(f"Failed to sync holidays for {country.iso_alpha2}: {str(e)}")
            results["errors"] += 1
            
    return results

async def sync_holidays(db: Session, iso2: str):
    """Sync holidays for a country from Nager.Date API with automatic translation"""
    current_year = date.today().year
    
    # Nager.Date API: https://date.nager.at/api/v3/PublicHolidays/2024/JP
    url = f"https://date.nager.at/api/v3/PublicHolidays/{current_year}/{iso2.upper()}"

    async with httpx.AsyncClient(timeout=15.0) as client:
        try:
            response = await client.get(url)
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
            # Translate if it's not already in Polish (Nager mostly returns English/Local)
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
