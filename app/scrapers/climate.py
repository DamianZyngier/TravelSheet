import httpx
from sqlalchemy.orm import Session
from .. import models
import asyncio
import logging
from collections import defaultdict

logger = logging.getLogger("uvicorn")

async def sync_country_climate(db: Session, country: models.Country, client: httpx.AsyncClient):
    if not country.latitude or not country.longitude:
        return {"skipped": True}
        
    try:
        url = (
            f"https://archive-api.open-meteo.com/v1/archive?"
            f"latitude={country.latitude}&longitude={country.longitude}&"
            f"start_date=2024-01-01&end_date=2024-12-31&"
            f"daily=temperature_2m_max,temperature_2m_min,precipitation_sum&timezone=GMT"
        )
        
        resp = await client.get(url)
        if resp.status_code == 200:
            data = resp.json()
            daily = data.get("daily", {})
            monthly_stats = defaultdict(lambda: {"temp_max": [], "temp_min": [], "rain": []})
            
            times = daily.get("time", [])
            max_temps = daily.get("temperature_2m_max", [])
            min_temps = daily.get("temperature_2m_min", [])
            precip = daily.get("precipitation_sum", [])
            
            if not times or len(times) < 300:
                return {"error": "Incomplete data"}

            for i in range(len(times)):
                try:
                    month = int(times[i].split("-")[1])
                    if i < len(max_temps) and max_temps[i] is not None: monthly_stats[month]["temp_max"].append(max_temps[i])
                    if i < len(min_temps) and min_temps[i] is not None: monthly_stats[month]["temp_min"].append(min_temps[i])
                    if i < len(precip) and precip[i] is not None: monthly_stats[month]["rain"].append(precip[i])
                except: continue
            
            months_with_data = [m for m in range(1, 13) if monthly_stats[m]["temp_max"]]
            if len(months_with_data) < 12:
                return {"error": "Incomplete monthly data"}

            db.query(models.Climate).filter(models.Climate.country_id == country.id).delete()
            for month in range(1, 13):
                stats = monthly_stats[month]
                avg_max = sum(stats["temp_max"]) / len(stats["temp_max"])
                avg_min = sum(stats["temp_min"]) / len(stats["temp_min"])
                total_rain = sum(stats["rain"])
                
                db.add(models.Climate(
                    country_id=country.id,
                    month=month,
                    avg_temp_max=int(round(avg_max)),
                    avg_temp_min=int(round(avg_min)),
                    avg_rain_mm=int(round(total_rain)),
                    season_type='N/A'
                ))
            db.commit()
            return {"status": "success"}
        elif resp.status_code == 429:
            return {"error": "Rate limit"}
        else:
            return {"error": f"HTTP {resp.status_code}"}
    except Exception as e:
        return {"error": str(e)}

async def sync_all_climate(db: Session, force: bool = False):
    countries = db.query(models.Country).all()
    results = {"synced": 0, "errors": 0, "skipped": 0}
    
    semaphore = asyncio.Semaphore(10)
    
    async def limited_sync(country, client):
        async with semaphore:
            if not force:
                existing = db.query(models.Climate).filter(models.Climate.country_id == country.id).first()
                if existing:
                    results["skipped"] += 1
                    return
            
            res = await sync_country_climate(db, country, client)
            if res.get("status") == "success":
                results["synced"] += 1
            elif not res.get("skipped"):
                results["errors"] += 1
                logger.debug(f"Climate error {country.iso_alpha2}: {res.get('error')}")

    logger.info(f"Starting parallel Climate sync for {len(countries)} countries...")
    async with httpx.AsyncClient(timeout=60.0) as client:
        await asyncio.gather(*(limited_sync(c, client) for c in countries))
                
    return results
