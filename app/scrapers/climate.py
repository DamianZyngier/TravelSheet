import httpx
from sqlalchemy.orm import Session
from .. import models
import logging
import asyncio
from datetime import date
from collections import defaultdict

logger = logging.getLogger("uvicorn")

async def sync_all_climate(db: Session, force: bool = False):
    """Sync climate data for all countries in the database using Open-Meteo"""
    countries = db.query(models.Country).all()
    results = {"synced": 0, "errors": 0, "skipped": 0}
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        for country in countries:
            if not country.latitude or not country.longitude:
                continue
            
            # Skip if already has data unless force is True
            if not force:
                existing = db.query(models.Climate).filter(models.Climate.country_id == country.id).first()
                if existing:
                    results["skipped"] += 1
                    continue
                
            try:
                # Fetch data for the whole year 2024
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
                    
                    # Group by month
                    monthly_stats = defaultdict(lambda: {"temp_max": [], "temp_min": [], "rain": []})
                    
                    times = daily.get("time", [])
                    max_temps = daily.get("temperature_2m_max", [])
                    min_temps = daily.get("temperature_2m_min", [])
                    precip = daily.get("precipitation_sum", [])
                    
                    for i in range(len(times)):
                        month = int(times[i].split("-")[1])
                        if max_temps[i] is not None: monthly_stats[month]["temp_max"].append(max_temps[i])
                        if min_temps[i] is not None: monthly_stats[month]["temp_min"].append(min_temps[i])
                        if precip[i] is not None: monthly_stats[month]["rain"].append(precip[i])
                    
                    # Clear existing records
                    db.query(models.Climate).filter(models.Climate.country_id == country.id).delete()
                    
                    # Calculate and save averages
                    for month in range(1, 13):
                        stats = monthly_stats[month]
                        if not stats["temp_max"]: continue
                        
                        avg_max = sum(stats["temp_max"]) / len(stats["temp_max"])
                        avg_min = sum(stats["temp_min"]) / len(stats["temp_min"])
                        total_rain = sum(stats["rain"])
                        
                        climate_entry = models.Climate(
                            country_id=country.id,
                            month=month,
                            avg_temp_max=int(round(avg_max)),
                            avg_temp_min=int(round(avg_min)),
                            avg_rain_mm=int(round(total_rain)),
                            season_type='N/A'
                        )
                        db.add(climate_entry)
                    
                    db.commit()
                    results["synced"] += 1
                    logger.info(f"Synced climate for {country.iso_alpha2}")
                elif resp.status_code == 429:
                    logger.warning(f"Rate limit hit for {country.iso_alpha2}, stopping sync.")
                    return results
                else:
                    logger.error(f"Open-Meteo error for {country.iso_alpha2}: {resp.status_code}")
                    results["errors"] += 1
                
                # Politeness - Open-Meteo is free but let's be kind
                await asyncio.sleep(1.0)
                
            except Exception as e:
                logger.error(f"Error syncing climate for {country.iso_alpha2}: {e}")
                results["errors"] += 1
                
    return results
