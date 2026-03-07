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
    # Handle common name variations
    name = country.name.lower()
    if "republic of the" in name: name = name.replace("republic of the ", "")
    if "kingdom of" in name: name = name.replace("kingdom of ", "")
    return slugify(name)

async def sync_cdc_health(db: Session, country_iso2: str, client: httpx.AsyncClient, depth: int = 0):
    if depth > 2: return {"error": "Max recursion depth reached"}
    
    country = db.query(models.Country).filter(models.Country.iso_alpha2 == country_iso2.upper()).first()
    if not country: return {"error": "Country not found"}

    slug = get_cdc_slug(country)
    # CDC sometimes uses different prefixes/suffixes
    urls = [
        f"https://wwwnc.cdc.gov/travel/destinations/traveler/none/{slug}",
        f"https://wwwnc.cdc.gov/travel/destinations/traveler/none/{slug}-sar",
        f"https://wwwnc.cdc.gov/travel/destinations/traveler/none/{slug}-islands"
    ]
    
    for url in urls:
        try:
            resp = await client.get(url, headers=get_headers(accept="text/html"))
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.text, 'html.parser')
                # ... same processing logic ...
                vax_table = soup.select_one('table#dest-vm-a') or soup.select_one('table.disease') or soup.select_one('table.vax-list-table')
                
                required, suggested = [], []
                
                if not vax_table:
                    # Special case for countries that often don't have tables
                    if country_iso2.upper() in ['US', 'AQ', 'PL']:
                        required, suggested = [], ["Zalecane szczepienia rutynowe"]
                    else:
                        continue # Try next URL
                else:
                    rows = vax_table.select('tbody tr')
                    for row in rows:
                        cells = row.find_all('td')
                        if len(cells) >= 2:
                            name = cells[0].get_text(strip=True)
                            rec = cells[1].get_text(" ", strip=True) 
                            if any(word in rec.lower() for word in ["required", "mandatory"]):
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
            elif resp.status_code == 404:
                continue
            else:
                return {"error": f"CDC returned {resp.status_code}"}
        except Exception as e:
            return {"error": f"{type(e).__name__}: {str(e)}"}

    # Final Fallback to Parent
    if country.parent_id:
        parent = db.query(models.Country).get(country.parent_id)
        if parent:
            logger.info(f"CDC all URLs 404 for {country_iso2}, falling back to parent {parent.iso_alpha2}")
            return await sync_cdc_health(db, parent.iso_alpha2, client, depth + 1)
            
    return {"error": f"CDC returned 404 for all variants of {slug}"}

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
                logger.warning(f"CDC Sync Error ({country.iso_alpha2}): {res.get('error')}")

    logger.info(f"Starting parallel CDC sync for {len(countries)} countries...")
    async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
        await asyncio.gather(*(limited_sync(c, client) for c in countries))
        
    return results
