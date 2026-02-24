import httpx
from sqlalchemy.orm import Session
from .. import models
import asyncio
import logging

logger = logging.getLogger("uvicorn")

async def sync_wiki_attractions(db: Session, country_iso2: str):
    country = db.query(models.Country).filter(models.Country.iso_alpha2 == country_iso2.upper()).first()
    if not country: return {"error": "Country not found"}

    # Refined SPARQL
    query = f"""
    SELECT DISTINCT ?item ?itemLabel ?itemDescription ?sitelinks WHERE {{
      ?item wdt:P31/wdt:P279* wd:Q570116; 
            wdt:P17 ?country.
      ?country wdt:P297 "{country_iso2.upper()}".
      ?item wikibase:sitelinks ?sitelinks.
      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "pl,en". }}
    }}
    ORDER BY DESC(?sitelinks)
    LIMIT 15
    """

    url = "https://query.wikidata.org/sparql"
    headers = {
        "User-Agent": "TravelCheatsheet/1.0 (https://github.com/zyngi/TravelSheet)",
        "Accept": "application/sparql-results+json"
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            resp = await client.get(url, params={'query': query}, headers=headers)
            if resp.status_code != 200:
                return {"error": f"Wikidata error {resp.status_code}"}
            
            data = resp.json()
            results = data.get("results", {}).get("bindings", [])
            
            synced = 0
            for res in results:
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
            
            db.commit()
            return {"status": "success", "synced": synced}
        except Exception as e:
            return {"error": str(e)}

async def sync_all_wiki_attractions(db: Session):
    countries = db.query(models.Country).all()
    total = {"synced_countries": 0, "total_attractions": 0}
    for c in countries:
        res = await sync_wiki_attractions(db, c.iso_alpha2)
        if "status" in res:
            total["synced_countries"] += 1
            total["total_attractions"] += res["synced"]
        await asyncio.sleep(1.0)
    return total
