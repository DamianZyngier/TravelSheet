import httpx
from sqlalchemy.orm import Session
from .. import models
import asyncio
import logging

logger = logging.getLogger("uvicorn")

async def sync_wikidata_country_info(db: Session, country_iso2: str):
    """
    Fetches timezone and national dish for a specific country from Wikidata.
    """
    country = db.query(models.Country).filter(models.Country.iso_alpha2 == country_iso2.upper()).first()
    if not country: return {"error": "Country not found"}

    # SPARQL Query: Get timezone and national dish
    query = f"""
    SELECT ?timezoneLabel ?dishLabel WHERE {{
      ?country wdt:P297 "{country_iso2.upper()}".
      OPTIONAL {{ ?country wdt:P421 ?timezone. }}
      OPTIONAL {{ ?country wdt:P3646 ?dish. }}
      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "pl,en". }}
    }}
    LIMIT 1
    """

    url = "https://query.wikidata.org/sparql"
    headers = {
        "User-Agent": "TravelCheatsheet/1.0 (https://github.com/zyngi/TravelSheet)",
        "Accept": "application/sparql-results+json"
    }

    async with httpx.AsyncClient(timeout=20.0) as client:
        try:
            resp = await client.get(url, params={'query': query}, headers=headers)
            if resp.status_code == 200:
                data = resp.json()
                results = data.get("results", {}).get("bindings", [])
                if results:
                    r = results[0]
                    timezone = r.get("timezoneLabel", {}).get("value")
                    dish = r.get("dishLabel", {}).get("value")
                    
                    if timezone and not timezone.startswith("Q"):
                        country.timezone = timezone
                    if dish and not dish.startswith("Q"):
                        country.national_dish = dish
                    
                    db.commit()
                    return {"status": "success"}
            return {"error": f"Wikidata returned {resp.status_code}"}
        except Exception as e:
            return {"error": str(e)}

async def sync_all_wikidata_info(db: Session):
    countries = db.query(models.Country).all()
    results = {"synced": 0, "errors": 0}
    for c in countries:
        res = await sync_wikidata_country_info(db, c.iso_alpha2)
        if "status" in res: results["synced"] += 1
        else: results["errors"] += 1
        await asyncio.sleep(0.5)
    return results
