import httpx
from sqlalchemy.orm import Session
from .. import models
import json
import logging
import asyncio

logger = logging.getLogger("uvicorn")

async def sync_emergency_numbers(db: Session):
    """
    Syncs emergency numbers from https://emergencynumberapi.com/
    """
    countries = db.query(models.Country).all()
    results = {"synced": 0, "errors": 0}
    
    async with httpx.AsyncClient(timeout=15.0) as client:
        for country in countries:
            try:
                # The API uses ISO2 codes: https://emergencynumberapi.com/api/country/PL
                url = f"https://emergencynumberapi.com/api/country/{country.iso_alpha2}"
                resp = await client.get(url)
                
                if resp.status_code == 200:
                    data = resp.json()
                    
                    # Extract main numbers
                    emergency_data = {
                        "police": data.get("data", {}).get("police", {}).get("all", [None])[0],
                        "ambulance": data.get("data", {}).get("ambulance", {}).get("all", [None])[0],
                        "fire": data.get("data", {}).get("fire", {}).get("all", [None])[0],
                        "dispatch": data.get("data", {}).get("dispatch", {}).get("all", [None])[0],
                        "member_112": data.get("data", {}).get("member_112", False)
                    }
                    
                    # Update PracticalInfo
                    practical = db.query(models.PracticalInfo).filter(models.PracticalInfo.country_id == country.id).first()
                    if not practical:
                        practical = models.PracticalInfo(country_id=country.id)
                        db.add(practical)
                    
                    practical.emergency_numbers = json.dumps(emergency_data)
                    db.commit()
                    results["synced"] += 1
                else:
                    logger.debug(f"No emergency numbers found for {country.iso_alpha2}")
                
                # Rate limiting (the API is free but let's be polite)
                await asyncio.sleep(0.05)
                
            except Exception as e:
                logger.error(f"Error syncing emergency numbers for {country.iso_alpha2}: {e}")
                results["errors"] += 1
                
    return results
