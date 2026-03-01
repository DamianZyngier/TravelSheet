import httpx
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from .. import models
import asyncio
import logging
import re
from .utils import get_headers

logger = logging.getLogger("uvicorn")

async def sync_wiki_summary(db: Session, country_iso2: str, client: httpx.AsyncClient):
    """
    Fetches a professional summary from Wikipedia and national symbols from Wikidata.
    """
    country = db.query(models.Country).filter(models.Country.iso_alpha2 == country_iso2.upper()).first()
    if not country: return {"error": "Country not found"}

    name_pl = country.name_pl or country.name
    wiki_title = name_pl.replace(' ', '_')
    wiki_url = f"https://pl.wikipedia.org/api/rest_v1/page/summary/{wiki_title}"
    headers = get_headers()
    
    wikidata_query = f"""
    SELECT ?animalLabel ?flowerLabel WHERE {{
      ?country wdt:P297 "{country_iso2.upper()}".
      OPTIONAL {{ ?country wdt:P1582 ?animal. }}
      OPTIONAL {{ ?country wdt:P1801 ?flower. }}
      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "pl,en". }}
    }}
    LIMIT 1
    """

    # Wikipedia Part
    for attempt in range(2):
        try:
            wiki_resp = await client.get(wiki_url, headers=headers)
            if wiki_resp.status_code == 200:
                country.wiki_summary = wiki_resp.json().get("extract")
                break
            elif wiki_resp.status_code == 429:
                await asyncio.sleep(2)
            else:
                break
        except:
            break

    # Wikidata Part
    try:
        wd_resp = await client.get("https://query.wikidata.org/sparql", params={'query': wikidata_query}, headers=headers)
        if wd_resp.status_code == 200:
            bindings = wd_resp.json().get("results", {}).get("bindings", [])
            if bindings:
                b = bindings[0]
                animal = b.get("animalLabel", {}).get("value")
                flower = b.get("flowerLabel", {}).get("value")
                symbols = []
                if animal and not animal.startswith("Q"): symbols.append(f"Zwierzę: {animal}")
                if flower and not flower.startswith("Q"): symbols.append(f"Kwiat: {flower}")
                if symbols:
                    country.national_symbols = " • ".join(symbols)
    except:
        pass

    db.commit()
    return {"status": "success"}

async def sync_all_summaries(db: Session):
    countries = db.query(models.Country).all()
    results = {"success": 0, "errors": 0}
    
    semaphore = asyncio.Semaphore(20)
    
    async def limited_sync(country, client):
        async with semaphore:
            res = await sync_wiki_summary(db, country.iso_alpha2, client)
            if "status" in res:
                results["success"] += 1
            else:
                results["errors"] += 1

    logger.info(f"Starting parallel Wiki sync for {len(countries)} countries...")
    async with httpx.AsyncClient(timeout=20.0, follow_redirects=True) as client:
        await asyncio.gather(*(limited_sync(c, client) for c in countries))
        
    return results
