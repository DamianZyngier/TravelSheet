import httpx
from sqlalchemy.orm import Session
from .. import models
import asyncio
import logging
import re

logger = logging.getLogger("uvicorn")

async def sync_wiki_summary(db: Session, country_iso2: str):
    """
    Fetches a professional summary from Wikipedia and national symbols from Wikidata.
    """
    country = db.query(models.Country).filter(models.Country.iso_alpha2 == country_iso2.upper()).first()
    if not country: return {"error": "Country not found"}

    name_pl = country.name_pl or country.name
    
    # 1. Fetch Wikipedia Summary (Polish)
    # Using the official REST API for summaries
    wiki_url = f"https://pl.wikipedia.org/api/rest_v1/page/summary/{name_pl.replace(' ', '_')}"
    
    # 2. Wikidata Query for symbols
    wikidata_query = f"""
    SELECT ?animalLabel ?flowerLabel WHERE {{
      ?country wdt:P297 "{country_iso2.upper()}".
      OPTIONAL {{ ?country wdt:P1582 ?animal. }} # National animal
      OPTIONAL {{ ?country wdt:P1801 ?flower. }} # National flower
      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "pl,en". }}
    }}
    LIMIT 1
    """

    async with httpx.AsyncClient(timeout=15.0) as client:
        # Wikipedia Part
        try:
            wiki_resp = await client.get(wiki_url)
            if wiki_resp.status_code == 200:
                country.wiki_summary = wiki_resp.json().get("extract")
        except: pass

        # Wikidata Part
        try:
            wd_resp = await client.get("https://query.wikidata.org/sparql", params={'query': wikidata_query})
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
        except: pass

    db.commit()
    return {"status": "success"}

async def sync_all_summaries(db: Session):
    countries = db.query(models.Country).all()
    for c in countries:
        await sync_wiki_summary(db, c.iso_alpha2)
        await asyncio.sleep(0.3)
    return {"status": "done"}
