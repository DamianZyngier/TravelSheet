import httpx
from sqlalchemy.orm import Session
from .. import models
import asyncio
import logging
import json

logger = logging.getLogger("uvicorn")
# Wyciszenie logów HTTPX
logging.getLogger("httpx").setLevel(logging.WARNING)

async def sync_wikidata_batch(db: Session, countries: list[models.Country]):
    """Sync extended info for a batch of countries to speed up process"""
    if not countries: return
    
    country_map = {c.iso_alpha2.upper(): c for c in countries}
    isos = ' '.join([f'"{iso}"' for iso in country_map.keys()])
    
    # Combined query for multiple countries
    query = f"""
    SELECT ?countryISO ?timezoneLabel ?dishLabel ?phoneCode ?ethnicLabel ?religionLabel ?religionPercent 
           ?animalLabel ?alcoholLabel ?lgbtqLabel ?idReqLabel ?airportLabel ?railwayLabel 
           ?hazardLabel WHERE {{
      VALUES ?countryISO {{ {isos} }}
      ?country wdt:P297 ?countryISO.
      OPTIONAL {{ ?country wdt:P421 ?timezone. }}
      OPTIONAL {{ ?country wdt:P3646 ?dish. }}
      OPTIONAL {{ ?country wdt:P442 ?phoneCode. }}
      OPTIONAL {{ ?country p:P172 [ ps:P172 ?ethnic; pq:P2107 ?ethnicPercent ]. }}
      OPTIONAL {{ ?country p:P140 [ ps:P140 ?religion; pq:P2107 ?religionPercent ]. }}
      OPTIONAL {{ ?country wdt:P2579 ?animal. }}
      OPTIONAL {{ ?country wdt:P3931 ?alcohol. }}
      OPTIONAL {{ ?country wdt:P91 ?lgbtq. }}
      OPTIONAL {{ ?country wdt:P3120 ?idReq. }}
      OPTIONAL {{ ?country wdt:P114 ?airport. }}
      OPTIONAL {{ ?country wdt:P1194 ?railway. }}
      OPTIONAL {{ ?country wdt:P1057 ?hazard. }}

      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "pl,en". 
        ?timezone rdfs:label ?timezoneLabel.
        ?dish rdfs:label ?dishLabel.
        ?ethnic rdfs:label ?ethnicLabel.
        ?religion rdfs:label ?religionLabel.
        ?animal rdfs:label ?animalLabel.
        ?alcohol rdfs:label ?alcoholLabel.
        ?lgbtq rdfs:label ?lgbtqLabel.
        ?idReq rdfs:label ?idReqLabel.
        ?airport rdfs:label ?airportLabel.
        ?railway rdfs:label ?railwayLabel.
        ?hazard rdfs:label ?hazardLabel.
      }}
    }}
    """

    url = "https://query.wikidata.org/sparql"
    headers = {
        "User-Agent": "TravelCheatsheet/1.0 (https://github.com/zyngi/TravelSheet)",
        "Accept": "application/sparql-results+json",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    async with httpx.AsyncClient(timeout=120.0) as client:
        try:
            resp = await client.post(url, data={'query': query}, headers=headers)
            if resp.status_code != 200:
                logger.error(f"Wikidata batch error {resp.status_code}")
                return
            
            data = resp.json()
            results = data.get("results", {}).get("bindings", [])
            
            # Group results by ISO
            grouped_results = {}
            for res in results:
                iso = res.get("countryISO", {}).get("value")
                if iso not in grouped_results: grouped_results[iso] = []
                grouped_results[iso].append(res)
            
            for iso, bindings in grouped_results.items():
                if iso not in country_map: continue
                country = country_map[iso]
                
                ethnics = set()
                animals = set()
                hazards = set()
                religions = {}
                
                for r in bindings:
                    if not country.timezone: country.timezone = r.get("timezoneLabel", {}).get("value")
                    if not country.national_dish: country.national_dish = r.get("dishLabel", {}).get("value")
                    if not country.phone_code: country.phone_code = r.get("phoneCode", {}).get("value")
                    
                    if not country.alcohol_status: country.alcohol_status = r.get("alcoholLabel", {}).get("value")
                    if not country.lgbtq_status: country.lgbtq_status = r.get("lgbtqLabel", {}).get("value")
                    if not country.id_requirement: country.id_requirement = r.get("idReqLabel", {}).get("value")
                    if not country.main_airport: country.main_airport = r.get("airportLabel", {}).get("value")
                    if not country.railway_info: country.railway_info = r.get("railwayLabel", {}).get("value")

                    ethnic = r.get("ethnicLabel", {}).get("value")
                    if ethnic and not ethnic.startswith("Q"): ethnics.add(ethnic)
                    
                    animal = r.get("animalLabel", {}).get("value")
                    if animal and not animal.startswith("Q"): animals.add(animal)

                    hazard = r.get("hazardLabel", {}).get("value")
                    if hazard and not hazard.startswith("Q"): hazards.add(hazard)
                    
                    rel = r.get("religionLabel", {}).get("value")
                    perc = r.get("religionPercent", {}).get("value")
                    if rel and perc:
                        religions[rel] = max(religions.get(rel, 0), float(perc))

                if ethnics: country.ethnic_groups = ", ".join(sorted(list(ethnics))[:5])
                if animals: country.unique_animals = ", ".join(sorted(list(animals))[:5])
                if hazards: country.natural_hazards = ", ".join(sorted(list(hazards))[:5])
                
                # FALLBACKS
                if not country.popular_apps:
                    if country.continent == 'Europe': country.popular_apps = "WhatsApp, Messenger, Instagram"
                    elif country.continent == 'Asia': country.popular_apps = "WhatsApp, WeChat, Line, Telegram"
                    elif country.continent == 'Americas': country.popular_apps = "WhatsApp, Messenger, Instagram"
                    elif country.continent == 'Africa': country.popular_apps = "WhatsApp, Facebook"
                    else: country.popular_apps = "WhatsApp, Messenger"
                
                if not country.id_requirement:
                    if country.entry_req:
                        if country.entry_req.id_card_allowed: country.id_requirement = "Dowód osobisty lub Paszport"
                        elif country.entry_req.passport_required: country.id_requirement = "Paszport"
                        else: country.id_requirement = "Paszport (zalecany)"
                    else:
                        EU_EEA = ['AT', 'BE', 'BG', 'HR', 'CY', 'CZ', 'DK', 'EE', 'FI', 'FR', 'DE', 'GR', 'HU', 'IE', 'IT', 'LV', 'LT', 'LU', 'MT', 'NL', 'PL', 'PT', 'RO', 'SK', 'SI', 'ES', 'SE', 'IS', 'LI', 'NO', 'CH']
                        country.id_requirement = "Dowód osobisty lub Paszport" if country.iso_alpha2.upper() in EU_EEA else "Paszport"
                
                if religions:
                    db.query(models.Religion).filter(models.Religion.country_id == country.id).delete()
                    for name, p in religions.items():
                        db.add(models.Religion(country_id=country.id, name=name, percentage=p))

            db.commit()
        except Exception as e:
            logger.error(f"Batch sync error: {e}")

async def sync_things_batch(db: Session, countries: list[models.Country]):
    if not countries: return
    country_map = {c.iso_alpha2.upper(): c for c in countries}
    isos = ' '.join([f'"{iso}"' for iso in country_map.keys()])
    
    query = f"""
    SELECT DISTINCT ?countryISO ?thingLabel WHERE {{
      VALUES ?countryISO {{ {isos} }}
      ?country wdt:P297 ?countryISO.
      ?thing wdt:P31/wdt:P279* wd:Q570116;
             wdt:P17 ?country.
      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "pl,en". }}
    }}
    """
    url = "https://query.wikidata.org/sparql"
    headers = {"User-Agent": "TravelSheet/1.0", "Accept": "application/sparql-results+json", "Content-Type": "application/x-www-form-urlencoded"}
    
    async with httpx.AsyncClient(timeout=120.0) as client:
        try:
            resp = await client.post(url, data={'query': query}, headers=headers)
            if resp.status_code == 200:
                data = resp.json().get("results", {}).get("bindings", [])
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
        except Exception as e:
            logger.error(f"Things batch error: {e}")

async def sync_all_wikidata_info(db: Session):
    countries = db.query(models.Country).all()
    batch_size = 20
    
    print(f"Syncing extended info in batches of {batch_size}...")
    for i in range(0, len(countries), batch_size):
        batch = countries[i : i + batch_size]
        print(f"Progress: {i}/{len(countries)} countries...")
        await sync_wikidata_batch(db, batch)
        await sync_things_batch(db, batch)
        await asyncio.sleep(1.0)
    
    return {"status": "done"}

# Keep this for backward compatibility or single country updates
async def sync_wikidata_country_info(db: Session, country_iso2: str):
    country = db.query(models.Country).filter(models.Country.iso_alpha2 == country_iso2.upper()).first()
    if country:
        await sync_wikidata_batch(db, [country])
        await sync_things_batch(db, [country])
    return {"status": "done"}
