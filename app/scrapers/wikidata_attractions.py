import httpx
from sqlalchemy.orm import Session
from .. import models
import asyncio
import logging
from .utils import async_sparql_get

logger = logging.getLogger("uvicorn")
# Wyciszenie logów HTTPX
logging.getLogger("httpx").setLevel(logging.WARNING)

async def sync_wiki_attractions_batch(db: Session, countries: list[models.Country]):
    """Sync attractions for a batch of countries to speed up process"""
    if not countries: return
    
    country_map = {c.iso_alpha2.upper(): c for c in countries}
    isos = ' '.join([f'"{iso}"' for iso in country_map.keys()])
    
    # Ultra-simplified query: only items with many sitelinks
    query = f"""
    SELECT DISTINCT ?countryISO ?itemLabel WHERE {{
      VALUES ?countryISO {{ {isos} }}
      ?country wdt:P297 ?countryISO.
      ?item wdt:P31/wdt:P279* wd:Q570116; 
            wdt:P17 ?country;
            wikibase:sitelinks ?sitelinks.
      FILTER(?sitelinks > 50)
      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "pl,en". }}
    }}
    LIMIT 20
    """

    results = await async_sparql_get(query, "Wiki Attractions")
    if not results:
        return
    
    counts = {iso: 0 for iso in country_map.keys()}
    
    for res in results:
        iso = res.get("countryISO", {}).get("value")
        if not iso or iso not in counts or counts[iso] >= 5: continue
        
        country = country_map[iso]
        name = res.get("itemLabel", {}).get("value")
        
        if not name or name.startswith("Q"): continue

        existing = db.query(models.Attraction).filter(
            models.Attraction.country_id == country.id,
            models.Attraction.name == name
        ).first()
        
        if not existing:
            db.add(models.Attraction(
                country_id=country.id,
                name=name,
                category='Wiki Attraction',
                is_must_see=True,
                is_unique=False
            ))
            counts[iso] += 1
        else:
            from sqlalchemy.sql import func
            existing.last_updated = func.now()
    
    db.commit()

async def sync_all_wiki_attractions(db: Session):
    countries = db.query(models.Country).all()
    total = {"success": 0, "errors": 0}
    
    # SINGLE country batches because Wikidata is struggling
    batch_size = 1
    for i in range(0, len(countries), batch_size):
        batch = countries[i : i + batch_size]
        if (i + 1) % 10 == 0:
            logger.info(f"Syncing Wiki attractions progress: {i+1}/{len(countries)}...")
        try:
            await sync_wiki_attractions_batch(db, batch)
            total["success"] += len(batch)
        except Exception as e:
            logger.error(f"Error in batch sync: {e}")
            total["errors"] += len(batch)
        await asyncio.sleep(1.0) # Short sleep between many small queries
        
    return total
