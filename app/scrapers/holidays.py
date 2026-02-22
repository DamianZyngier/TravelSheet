import httpx
from sqlalchemy.orm import Session
from .. import models
from datetime import date
import asyncio

async def sync_holidays(db: Session, iso2: str):
    """Sync holidays for a country from OpenHolidays API"""
    
    current_year = date.today().year
    url = f"https://openholidaysapi.org/PublicHolidays?countryIsoCode={iso2.upper()}&validFrom={current_year}-01-01&validTo={current_year}-12-31&languageIsoCode=PL"

    async with httpx.AsyncClient(timeout=15.0) as client:
        try:
            response = await client.get(url)
            if response.status_code == 404:
                # Retry with English if Polish not available
                url = url.replace("languageIsoCode=PL", "languageIsoCode=EN")
                response = await client.get(url)
            
            response.raise_for_status()
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
            # OpenHolidays returns names as a list of localized names
            names = h.get('name', [])
            name_pl = next((n.get('text') for n in names if n.get('language') == 'PL'), None)
            name_en = next((n.get('text') for n in names if n.get('language') == 'EN'), names[0].get('text') if names else 'Unknown')
            
            holiday = models.Holiday(
                country_id=country.id,
                name=name_pl or name_en,
                name_local=h.get('name', [{}])[0].get('text'),
                date=date.fromisoformat(h.get('startDate')),
                type='Public'
            )
            db.add(holiday)
            synced += 1
        except:
            continue

    db.commit()
    return {"status": "success", "synced": synced}
