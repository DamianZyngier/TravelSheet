import requests
from bs4 import BeautifulSoup
from sqlalchemy.orm import Session
from .. import models
import asyncio
import logging
import re

logger = logging.getLogger("uvicorn")

WIKI_NAME_MAP = {
    "Congo (Democratic Republic of)": "CD",
    "Congo (Republic of)": "CG",
    "Democratic Republic of the Congo": "CD",
    "Republic of the Congo": "CG",
    "DR Congo": "CD",
    "Congo": "CG"
}

async def sync_all_visas(db: Session):
    url = "https://en.wikipedia.org/wiki/Visa_requirements_for_Polish_citizens"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"}
    
    try:
        resp = requests.get(url, headers=headers, timeout=30)
        if resp.status_code != 200:
            return {"error": f"Wiki returned {resp.status_code}"}
        
        soup = BeautifulSoup(resp.content, 'html.parser')
        target_table = None
        all_tables = soup.find_all('table')
        
        for table in all_tables:
            text = table.get_text().lower()
            if "visa requirement" in text and "country" in text:
                rows = table.find_all('tr')
                if len(rows) > 150:
                    target_table = table
                    break
        
        if not target_table:
            return {"error": "Could not find main visa table"}

        synced = 0
        rows = target_table.find_all('tr')
        
        for row in rows:
            cols = row.find_all(['td', 'th'])
            if len(cols) < 2: continue
            
            wiki_name = cols[0].get_text(strip=True)
            if "country" in wiki_name.lower(): continue 
            
            wiki_name = re.sub(r'\[.*?\]', '', wiki_name).strip()
            wiki_name = wiki_name.split('(')[0].strip()
            
            requirement = cols[1].get_text(strip=True)
            
            iso2 = WIKI_NAME_MAP.get(wiki_name)
            country = None
            if iso2:
                country = db.query(models.Country).filter(models.Country.iso_alpha2 == iso2).first()
            if not country:
                country = db.query(models.Country).filter(
                    (models.Country.name == wiki_name) | (models.Country.name_pl == wiki_name)
                ).first()
            if not country:
                country = db.query(models.Country).filter(models.Country.name.ilike(f"%{wiki_name}%")).first()

            if country:
                status = "Wiza wymagana"
                is_req = True
                req_lower = requirement.lower()
                
                if any(x in req_lower for x in ["not required", "visa-free", "freedom of movement"]):
                    status = "Wiza niepotrzebna"
                    is_req = False
                elif "on arrival" in req_lower:
                    status = "Visa on arrival"
                    is_req = True
                elif any(x in req_lower for x in ["evisa", "e-visa", "electronic"]):
                    status = "e-Visa"
                    is_req = True
                elif any(x in req_lower for x in ["eta", "estavisa"]):
                    status = "e-Visa / ETA"
                    is_req = True
                
                entry = db.query(models.EntryRequirement).filter(models.EntryRequirement.country_id == country.id).first()
                if not entry:
                    entry = models.EntryRequirement(country_id=country.id)
                    db.add(entry)
                
                entry.visa_status = status
                entry.visa_required = is_req
                synced += 1
        
        db.commit()
        return {"status": "success", "synced": synced}
    except Exception as e:
        return {"error": str(e)}
