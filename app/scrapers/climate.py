import logging
import asyncio
from sqlalchemy.orm import Session
from .. import models
from .base import BaseScraper
from collections import defaultdict

logger = logging.getLogger("uvicorn")

class ClimateScraper(BaseScraper):
    def __init__(self, db: Session):
        super().__init__(db, concurrency=2, timeout=60.0)
        self.rate_limit_delay = 1.0  # Open-Meteo is sensitive

    async def sync_country(self, country: models.Country):
        # Coordinates
        lat, lon = country.latitude, country.longitude
        if lat is None or lon is None:
            return {"error": "Missing coordinates"}

        url = "https://archive-api.open-meteo.com/v1/archive"
        params = {
            "latitude": float(lat),
            "longitude": float(lon),
            "start_date": "2023-01-01",
            "end_date": "2023-12-31",
            "daily": ["temperature_2m_max", "temperature_2m_min", "rain_sum"],
            "timezone": "auto"
        }

        try:
            resp = await self.client.get(url, params=params)
            if resp.status_code != 200:
                return {"error": f"Open-Meteo returned {resp.status_code}"}
            
            data = resp.json().get("daily", {})
            if not data:
                return {"error": "No daily data in response"}

            # Aggregate by month
            months = defaultdict(lambda: {"max": [], "min": [], "rain": []})
            for i, date_str in enumerate(data.get("time", [])):
                month = int(date_str.split("-")[1])
                if data["temperature_2m_max"][i] is not None:
                    months[month]["max"].append(data["temperature_2m_max"][i])
                if data["temperature_2m_min"][i] is not None:
                    months[month]["min"].append(data["temperature_2m_min"][i])
                if data["rain_sum"][i] is not None:
                    months[month]["rain"].append(data["rain_sum"][i])

            # Update DB
            self.db.query(models.Climate).filter(models.Climate.country_id == country.id).delete()
            
            for month, vals in months.items():
                if not vals["max"]: continue
                
                avg_max = sum(vals["max"]) / len(vals["max"])
                avg_min = sum(vals["min"]) / len(vals["min"])
                total_rain = sum(vals["rain"])
                
                # Simple season detection
                season = "shoulder"
                if avg_max > 25 and total_rain < 50: season = "dry"
                elif total_rain > 150: season = "wet"

                db_climate = models.Climate(
                    country_id=country.id,
                    month=month,
                    avg_temp_max=int(avg_max),
                    avg_temp_min=int(avg_min),
                    avg_rain_mm=int(total_rain),
                    season_type=season
                )
                self.db.add(db_climate)
            
            self.db.commit()
            return {"status": "success"}
        except Exception as e:
            return {"error": str(e)}

async def sync_all_climate(db: Session, force: bool = False):
    countries = db.query(models.Country).all()
    scraper = ClimateScraper(db)
    return await scraper.run(countries)
