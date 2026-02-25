import httpx
from bs4 import BeautifulSoup
from sqlalchemy.orm import Session
from .. import models
import asyncio
import logging
from .utils import CDC_MAPPING, slugify, get_headers

logger = logging.getLogger("uvicorn")

def get_cdc_slug(country):
    if country.iso_alpha2 in CDC_MAPPING:
        return CDC_MAPPING[country.iso_alpha2]
    return slugify(country.name)

async def sync_cdc_health(db: Session, country_iso2: str):
    country = db.query(models.Country).filter(models.Country.iso_alpha2 == country_iso2.upper()).first()
    if not country: return {"error": "Country not found"}

    slug = get_cdc_slug(country)
    url = f"https://wwwnc.cdc.gov/travel/destinations/traveler/none/{slug}"
    
    async with httpx.AsyncClient(timeout=20.0, follow_redirects=True) as client:
        try:
            resp = await client.get(url, headers=get_headers())
            if resp.status_code != 200:
                return {"error": f"CDC returned {resp.status_code} for {slug}"}
            
            soup = BeautifulSoup(resp.text, 'html.parser')
            vax_table = soup.select_one('table.vax-list-table')
            
            if not vax_table:
                return {"error": "No vax table found"}

            required, suggested = [], []
            rows = vax_table.select('tbody tr')
            for row in rows:
                cells = row.find_all('td')
                if len(cells) >= 2:
                    name = cells[0].get_text(strip=True)
                    rec = cells[1].get_text(strip=True)
                    if any(word in rec for word in ["Required", "Mandatory"]):
                        required.append(name)
                    else:
                        suggested.append(name)

            practical = db.query(models.PracticalInfo).filter(models.PracticalInfo.country_id == country.id).first()
            if not practical:
                practical = models.PracticalInfo(country_id=country.id)
                db.add(practical)
            
            practical.vaccinations_required = ", ".join(required) if required else ""
            practical.vaccinations_suggested = ", ".join(suggested) if suggested else ""
            db.commit()
            return {"status": "success"}
        except Exception as e:
            return {"error": str(e)}

async def sync_all_cdc(db: Session):
    countries = db.query(models.Country).all()
    results = {"synced": 0, "errors": 0}
    for c in countries:
        res = await sync_cdc_health(db, c.iso_alpha2)
        if "status" in res:
            results["synced"] += 1
            logger.info(f"CDC Synced: {c.iso_alpha2}")
        else:
            results["errors"] += 1
            logger.debug(f"CDC Error {c.iso_alpha2}: {res['error']}")
        await asyncio.sleep(0.2)
    return results
