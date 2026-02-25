import httpx
from sqlalchemy.orm import Session
from .. import models
import asyncio
import logging

logger = logging.getLogger("uvicorn")

async def sync_wiki_attractions_batch(db: Session, countries: list[models.Country]):
    """Sync attractions for a batch of countries to speed up process"""
    if not countries: return
    
    country_map = {c.iso_alpha2.upper(): c for c in countries}
    isos = ' '.join([f'"{iso}"' for iso in country_map.keys()])
    
    query = f"""
    SELECT DISTINCT ?countryISO ?item ?itemLabel ?itemDescription ?sitelinks WHERE {{
      VALUES ?countryISO {{ {isos} }}
      ?country wdt:P297 ?countryISO.
      ?item wdt:P31/wdt:P279* wd:Q570116; 
            wdt:P17 ?country.
      ?item wikibase:sitelinks ?sitelinks.
      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "pl,en". }}
    }}
    ORDER BY DESC(?sitelinks)
    """

    url = "https://query.wikidata.org/sparql"
    headers = {
        "User-Agent": "TravelCheatsheet/1.0 (https://github.com/zyngi/TravelSheet)",
        "Accept": "application/sparql-results+json"
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            resp = await client.get(url, params={'query': query}, headers=headers)
            if resp.status_code != 200:
                logger.error(f"Wikidata batch error {resp.status_code}")
                return
            
            data = resp.json()
            results = data.get("results", {}).get("bindings", [])
            
            synced = 0
            # To avoid huge number of attractions, we'll only take top 10 per country from the results
            counts = {iso: 0 for iso in country_map.keys()}
            
            for res in results:
                iso = res.get("countryISO", {}).get("value")
                if not iso or counts[iso] >= 10: continue
                
                country = country_map[iso]
                name = res.get("itemLabel", {}).get("value")
                description = res.get("itemDescription", {}).get("value")
                
                if not name or name.startswith("Q"): continue

                existing = db.query(models.Attraction).filter(
                    models.Attraction.country_id == country.id,
                    models.Attraction.name == name
                ).first()
                
                if not existing:
                    db.add(models.Attraction(
                        country_id=country.id,
                        name=name,
                        description=description,
                        category='Wiki Attraction',
                        is_must_see=True,
                        is_unique=False
                    ))
                    synced += 1
                    counts[iso] += 1
            
            db.commit()
            logger.info(f"Batch sync: Added {synced} attractions for {len(countries)} countries.")
        except Exception as e:
            logger.error(f"Batch sync error: {e}")

async def sync_all_wiki_attractions(db: Session):
    countries = db.query(models.Country).all()
    total = {"synced_countries": len(countries), "total_attractions": 0}
    
    # Process in batches of 10 countries
    batch_size = 10
    for i in range(0, len(countries), batch_size):
        batch = countries[i : i + batch_size]
        logger.info(f"Syncing Wiki attractions batch {i//batch_size + 1}/{(len(countries)+batch_size-1)//batch_size}")
        await sync_wiki_attractions_batch(db, batch)
        # Still sleep a bit to be nice to Wikidata
        await asyncio.sleep(2.0)
        
    # Count total at the end
    total["total_attractions"] = db.query(models.Attraction).filter(models.Attraction.category == 'Wiki Attraction').count()
    return total
