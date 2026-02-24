import httpx
from bs4 import BeautifulSoup
from sqlalchemy.orm import Session
from .. import models
import asyncio
import logging
import re

logger = logging.getLogger("uvicorn")

async def sync_all_visas(db: Session):
    """
    Scrapes detailed visa requirements for Polish citizens from Wikipedia.
    """
    url = "https://en.wikipedia.org/wiki/Visa_requirements_for_Polish_citizens"
    headers = {"User-Agent": "TravelCheatsheet/1.0"}
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            resp = await client.get(url)
            if resp.status_code != 200:
                return {"error": f"Wiki returned {resp.status_code}"}
            
            soup = BeautifulSoup(resp.text, 'html.parser')
            table = soup.find('table', {'class': 'wikitable'})
            if not table:
                return {"error": "Visa table not found"}

            synced = 0
            rows = table.find_all('tr')[1:] # Skip header
            
            for row in rows:
                cols = row.find_all(['td', 'th'])
                if len(cols) < 2: continue
                
                country_name = cols[0].get_text(strip=True)
                requirement = cols[1].get_text(strip=True)
                
                # Cleanup country name (remove flags/notes)
                country_name = re.sub(r'\[.*?\]', '', country_name).strip()
                
                # Try to find country in our DB
                # Note: Wiki uses common names, might need mapping or fuzzy match
                country = db.query(models.Country).filter(
                    (models.Country.name == country_name) | 
                    (models.Country.name_pl == country_name)
                ).first()
                
                if not country:
                    # Fallback: check if wiki name is in our name
                    country = db.query(models.Country).filter(models.Country.name.ilike(f"%{country_name}%")).first()

                if country:
                    status = "Wiza wymagana"
                    req_lower = requirement.lower()
                    
                    if "visa not required" in req_lower or "visa-free" in req_lower or "freedom of movement" in req_lower:
                        status = "Wiza niepotrzebna"
                    elif "visa on arrival" in req_lower:
                        status = "Visa on arrival"
                    elif "evisa" in req_lower or "e-visa" in req_lower or "electronic" in req_lower:
                        status = "e-Visa"
                    elif "eta" in req_lower or "estavisa" in req_lower:
                        status = "e-Visa / ETA"
                    
                    # Store
                    entry = db.query(models.EntryRequirement).filter(models.EntryRequirement.country_id == country.id).first()
                    if not entry:
                        entry = models.EntryRequirement(country_id=country.id)
                        db.add(entry)
                    
                    entry.visa_status = status
                    entry.visa_required = (status == "Wiza wymagana")
                    synced += 1
            
            db.commit()
            return {"status": "success", "synced": synced}
        except Exception as e:
            logger.error(f"Visa sync error: {e}")
            return {"error": str(e)}
