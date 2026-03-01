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

async def sync_cdc_health(db: Session, country_iso2: str, client: httpx.AsyncClient):
    country = db.query(models.Country).filter(models.Country.iso_alpha2 == country_iso2.upper()).first()
    if not country: return {"error": "Country not found"}

    slug = get_cdc_slug(country)
    url = f"https://wwwnc.cdc.gov/travel/destinations/traveler/none/{slug}"
    
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
    
    semaphore = asyncio.Semaphore(15)
    
    async def limited_sync(country, client):
        async with semaphore:
            res = await sync_cdc_health(db, country.iso_alpha2, client)
            if "status" in res:
                results["synced"] += 1
            else:
                results["errors"] += 1
                logger.debug(f"CDC Error {country.iso_alpha2}: {res['error']}")

    logger.info(f"Starting parallel CDC sync for {len(countries)} countries...")
    async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
        await asyncio.gather(*(limited_sync(c, client) for c in countries))
        
    return results
