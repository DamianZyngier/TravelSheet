import httpx
from sqlalchemy.orm import Session
from .. import models
from datetime import date
import asyncio
import logging
from typing import Any

from .base import BaseScraper
from .utils import translate_to_pl, get_headers

logger = logging.getLogger("uvicorn")

class HolidayScraper(BaseScraper):
    """Sync holidays for a country from Nager.Date API with automatic translation"""
    def __init__(self, db: Session, concurrency: int = 5, timeout: float = 45.0):
        super().__init__(db, concurrency, timeout)

    async def sync_country(self, country: models.Country) -> Any:
        current_year = date.today().year
        iso2 = country.iso_alpha2.upper()
        
        if iso2 == 'XK':
            return {"status": "skipped", "reason": "Kosovo not supported by Nager.Date"}
        
        url = f"https://date.nager.at/api/v3/PublicHolidays/{current_year}/{iso2}"

        try:
            response = await self.client.get(url, headers=get_headers())
            if response.status_code == 204:
                return {"status": "success", "data": []}
            if response.status_code != 200:
                return {"error": f"HTTP {response.status_code}"}
            holidays_data = response.json()
        except Exception as e:
            return {"error": str(e)}

        # Delete existing holidays for the current year
        self.db.query(models.Holiday).filter(
            models.Holiday.country_id == country.id,
            models.Holiday.date >= date(current_year, 1, 1),
            models.Holiday.date <= date(current_year, 12, 31)
        ).delete()

        if not isinstance(holidays_data, list):
            holidays_data = []

        for h in holidays_data:
            try:
                original_name = h.get('name') or h.get('localName')
                name_pl = translate_to_pl(original_name)
                
                self.db.add(models.Holiday(
                    country_id=country.id,
                    name=name_pl,
                    name_local=h.get('localName'),
                    date=date.fromisoformat(h.get('date')),
                    type='Public'
                ))
            except Exception as e:
                logger.debug(f"Error adding holiday for {iso2}: {e}")
                continue

        self.db.commit()
        return {"status": "success", "count": len(holidays_data)}

async def sync_holidays(db: Session, iso2: str, client: httpx.AsyncClient):
    """Legacy wrapper for syncing holidays for a single country"""
    scraper = HolidayScraper(db)
    scraper.client = client
    country = db.query(models.Country).filter(models.Country.iso_alpha2 == iso2.upper()).first()
    if not country: return {"error": "Country not found"}
    return await scraper.sync_country(country)

async def sync_all_holidays(db: Session):
    """Legacy wrapper for syncing holidays for all countries"""
    scraper = HolidayScraper(db, concurrency=20)
    countries = db.query(models.Country).all()
    results = await scraper.run(countries)
    return {"synced": results["success"], "errors": results["errors"]}
