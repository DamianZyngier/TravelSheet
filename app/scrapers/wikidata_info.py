import httpx
from sqlalchemy.orm import Session
from .. import models
import asyncio
import logging
import json

logger = logging.getLogger("uvicorn")
logging.getLogger("httpx").setLevel(logging.WARNING)

async def run_sparql(client: httpx.AsyncClient, query: str):
    url = "https://query.wikidata.org/sparql"
    headers = {
        "User-Agent": "TravelSheet/1.1 (https://github.com/zyngi/TravelSheet)",
        "Accept": "application/sparql-results+json",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    try:
        resp = await client.post(url, data={'query': query}, headers=headers)
        if resp.status_code == 200:
            return resp.json().get("results", {}).get("bindings", [])
        elif resp.status_code == 429:
            logger.warning("Wikidata Rate Limit hit, sleeping...")
            await asyncio.sleep(5)
        else:
            logger.error(f"Wikidata error {resp.status_code}")
    except Exception as e:
        logger.error(f"SPARQL request error: {e}")
    return []

async def sync_wikidata_batch(db: Session, countries: list[models.Country], client: httpx.AsyncClient):
    """Sync info using multiple small queries for speed and stability"""
    if not countries: return
    country_map = {c.iso_alpha2.upper(): c for c in countries}
    isos = ' '.join([f'"{iso}"' for iso in country_map.keys()])
    
    # Query 1: Basic & Cultural
    q_basic = f"SELECT ?countryISO ?timezoneLabel ?dishLabel ?phoneCode ?ethnicLabel ?religionLabel ?religionPercent WHERE {{ VALUES ?countryISO {{ {isos} }} ?country wdt:P297 ?countryISO. OPTIONAL {{ ?country wdt:P421 ?timezone. }} OPTIONAL {{ ?country wdt:P3646 ?dish. }} OPTIONAL {{ ?country wdt:P442 ?phoneCode. }} OPTIONAL {{ ?country p:P172 [ ps:P172 ?ethnic; pq:P2107 ?ethnicPercent ]. }} OPTIONAL {{ ?country p:P140 [ ps:P140 ?religion; pq:P2107 ?religionPercent ]. }} SERVICE wikibase:label {{ bd:serviceParam wikibase:language 'pl,en'. }} }}"
    
    # Query 2: Law & Safety (Removed Animals)
    q_law = f"SELECT ?countryISO ?alcoholLabel ?lgbtqLabel ?idReqLabel ?hazardLabel WHERE {{ VALUES ?countryISO {{ {isos} }} ?country wdt:P297 ?countryISO. OPTIONAL {{ ?country wdt:P3931 ?alcohol. }} OPTIONAL {{ ?country wdt:P91 ?lgbtq. }} OPTIONAL {{ ?country wdt:P3120 ?idReq. }} OPTIONAL {{ ?country wdt:P1057 ?hazard. }} SERVICE wikibase:label {{ bd:serviceParam wikibase:language 'pl,en'. }} }}"

    # Query 3: Transport
    q_trans = f"SELECT ?countryISO ?airportLabel ?railwayLabel WHERE {{ VALUES ?countryISO {{ {isos} }} ?country wdt:P297 ?countryISO. OPTIONAL {{ ?country wdt:P114 ?airport. }} OPTIONAL {{ ?country wdt:P1194 ?railway. }} SERVICE wikibase:label {{ bd:serviceParam wikibase:language 'pl,en'. }} }}"

    # Run queries in parallel
    results = await asyncio.gather(
        run_sparql(client, q_basic),
        run_sparql(client, q_law),
        run_sparql(client, q_trans)
    )
    
    # Process Results
    for r in results[0]:
        iso = r.get("countryISO", {}).get("value")
        if iso not in country_map: continue
        c = country_map[iso]
        if not c.timezone: c.timezone = r.get("timezoneLabel", {}).get("value")
        if not c.national_dish: c.national_dish = r.get("dishLabel", {}).get("value")
        if not c.phone_code: c.phone_code = r.get("phoneCode", {}).get("value")
    
    for r in results[1]:
        iso = r.get("countryISO", {}).get("value")
        if iso not in country_map: continue
        c = country_map[iso]
        if not c.alcohol_status: c.alcohol_status = r.get("alcoholLabel", {}).get("value")
        if not c.lgbtq_status: c.lgbtq_status = r.get("lgbtqLabel", {}).get("value")
        if not c.id_requirement: c.id_requirement = r.get("idReqLabel", {}).get("value")

    for r in results[2]:
        iso = r.get("countryISO", {}).get("value")
        if iso not in country_map: continue
        c = country_map[iso]
        if not c.main_airport: c.main_airport = r.get("airportLabel", {}).get("value")
        if not c.railway_info: c.railway_info = r.get("railwayLabel", {}).get("value")

    # Post-process Fallbacks
    for c in countries:
        if not c.popular_apps:
            if c.continent == 'Europe': c.popular_apps = "WhatsApp, Messenger, Instagram"
            elif c.continent == 'Asia': c.popular_apps = "WhatsApp, WeChat, Line, Telegram"
            elif c.continent == 'Americas': c.popular_apps = "WhatsApp, Messenger, Instagram"
            elif c.continent == 'Africa': c.popular_apps = "WhatsApp, Facebook"
            else: c.popular_apps = "WhatsApp, Messenger"
        if not c.id_requirement:
            if c.entry_req:
                if c.entry_req.id_card_allowed: c.id_requirement = "Dowód osobisty lub Paszport"
                elif c.entry_req.passport_required: c.id_requirement = "Paszport"
                else: c.id_requirement = "Paszport (zalecany)"
            else:
                EU_EEA = ['AT', 'BE', 'BG', 'HR', 'CY', 'CZ', 'DK', 'EE', 'FI', 'FR', 'DE', 'GR', 'HU', 'IE', 'IT', 'LV', 'LT', 'LU', 'MT', 'NL', 'PL', 'PT', 'RO', 'SK', 'SI', 'ES', 'SE', 'IS', 'LI', 'NO', 'CH']
                c.id_requirement = "Dowód osobisty lub Paszport" if c.iso_alpha2.upper() in EU_EEA else "Paszport"
    
    db.commit()

async def sync_things_batch(db: Session, countries: list[models.Country], client: httpx.AsyncClient):
    if not countries: return
    country_map = {c.iso_alpha2.upper(): c for c in countries}
    isos = ' '.join([f'"{iso}"' for iso in country_map.keys()])
    
    query = f"SELECT DISTINCT ?countryISO ?thingLabel WHERE {{ VALUES ?countryISO {{ {isos} }} ?country wdt:P297 ?countryISO. ?thing wdt:P31/wdt:P279* wd:Q570116; wdt:P17 ?country. SERVICE wikibase:label {{ bd:serviceParam wikibase:language 'pl,en'. }} }}"
    
    data = await run_sparql(client, query)
    iso_things = {}
    for r in data:
        iso = r.get("countryISO", {}).get("value")
        val = r.get("thingLabel", {}).get("value")
        if iso and val and not val.startswith("Q"):
            if iso not in iso_things: iso_things[iso] = set()
            iso_things[iso].add(val)
    
    for iso, things in iso_things.items():
        if iso in country_map:
            country_map[iso].unique_things = ", ".join(sorted(list(things))[:5])
    db.commit()

async def sync_all_wikidata_info(db: Session):
    countries = db.query(models.Country).all()
    batch_size = 10
    
    print(f"Syncing extended info in batches of {batch_size}...")
    async with httpx.AsyncClient(timeout=120.0) as client:
        for i in range(0, len(countries), batch_size):
            batch = countries[i : i + batch_size]
            print(f"Progress: {i}/{len(countries)} countries...")
            await asyncio.gather(
                sync_wikidata_batch(db, batch, client),
                sync_things_batch(db, batch, client)
            )
            await asyncio.sleep(2.0)
    
    return {"status": "done"}

async def sync_wikidata_country_info(db: Session, country_iso2: str):
    country = db.query(models.Country).filter(models.Country.iso_alpha2 == country_iso2.upper()).first()
    if country:
        async with httpx.AsyncClient(timeout=120.0) as client:
            await sync_wikidata_batch(db, [country], client)
            await sync_things_batch(db, [country], client)
    return {"status": "done"}
