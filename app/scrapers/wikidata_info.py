import httpx
from sqlalchemy.orm import Session
from .. import models
import asyncio
import logging
from .utils import async_sparql_get

logger = logging.getLogger("uvicorn")
logging.getLogger("httpx").setLevel(logging.WARNING)

async def sync_wikidata_batch(db: Session, countries: list[models.Country]):
    """Sync info using multiple small queries for speed and stability"""
    if not countries: return
    country_map = {c.iso_alpha2.upper(): c for c in countries}
    isos = ' '.join([f'"{iso}"' for iso in country_map.keys()])
    
    # Query 1: Simple Info
    q_simple = f"SELECT ?countryISO ?timezoneLabel ?dishLabel ?phoneCode WHERE {{ VALUES ?countryISO {{ {isos} }} ?country wdt:P297 ?countryISO. OPTIONAL {{ ?country wdt:P421 ?timezone. }} OPTIONAL {{ ?country wdt:P3646 ?dish. }} OPTIONAL {{ ?country wdt:P442 ?phoneCode. }} SERVICE wikibase:label {{ bd:serviceParam wikibase:language 'pl,en'. }} }}"
    
    # Query 2: Cultural (Ethnics & Religions) - More lenient for religions
    q_cultural = f"SELECT ?countryISO ?ethnicLabel ?religionLabel ?religionPercent WHERE {{ VALUES ?countryISO {{ {isos} }} ?country wdt:P297 ?countryISO. OPTIONAL {{ ?country p:P172 [ ps:P172 ?ethnic; pq:P2107 ?ethnicPercent ]. }} OPTIONAL {{ ?country p:P140 ?relStatement. ?relStatement ps:P140 ?religion. OPTIONAL {{ ?relStatement pq:P2107 ?religionPercent. }} }} SERVICE wikibase:label {{ bd:serviceParam wikibase:language 'pl,en'. }} }}"
    
    # Query 3: Law & Safety
    q_law = f"SELECT ?countryISO ?animalLabel ?alcoholLabel ?lgbtqLabel ?idReqLabel ?hazardLabel WHERE {{ VALUES ?countryISO {{ {isos} }} ?country wdt:P297 ?countryISO. OPTIONAL {{ ?country wdt:P1584 ?animal. }} OPTIONAL {{ ?country wdt:P3931 ?alcohol. }} OPTIONAL {{ ?country wdt:P91 ?lgbtq. }} OPTIONAL {{ ?country wdt:P3120 ?idReq. }} OPTIONAL {{ ?country wdt:P1057 ?hazard. }} SERVICE wikibase:label {{ bd:serviceParam wikibase:language 'pl,en'. }} }}"

    # Query 4: Transport
    q_trans = f"SELECT ?countryISO ?airportLabel ?railwayLabel WHERE {{ VALUES ?countryISO {{ {isos} }} ?country wdt:P297 ?countryISO. OPTIONAL {{ ?country wdt:P114 ?airport. }} OPTIONAL {{ ?country wdt:P1194 ?railway. }} SERVICE wikibase:label {{ bd:serviceParam wikibase:language 'pl,en'. }} }}"

    # Run queries
    # sequential to avoid overwhelming Wikidata
    results = [
        await async_sparql_get(q_simple, "Simple Info"),
        await async_sparql_get(q_cultural, "Cultural Info"),
        await async_sparql_get(q_law, "Law Info"),
        await async_sparql_get(q_trans, "Transport Info")
    ]
    
    # Data containers for grouped processing
    country_religions = {} # ISO -> {name: percent}
    country_ethnics = {} # ISO -> set
    country_hazards = {} # ISO -> set

    # Process Results
    # 1. Simple Info
    for r in results[0]:
        iso = r.get("countryISO", {}).get("value")
        if iso not in country_map: continue
        c = country_map[iso]
        if not c.timezone: c.timezone = r.get("timezoneLabel", {}).get("value")
        if not c.national_dish: c.national_dish = r.get("dishLabel", {}).get("value")
        if not c.phone_code: c.phone_code = r.get("phoneCode", {}).get("value")
    
    # 2. Cultural
    for r in results[1]:
        iso = r.get("countryISO", {}).get("value")
        if iso not in country_map: continue
        
        ethnic = r.get("ethnicLabel", {}).get("value")
        if ethnic and not ethnic.startswith("Q"):
            if iso not in country_ethnics: country_ethnics[iso] = set()
            country_ethnics[iso].add(ethnic)
            
        rel = r.get("religionLabel", {}).get("value")
        perc = r.get("religionPercent", {}).get("value")
        if rel and not rel.startswith("Q"):
            if iso not in country_religions: country_religions[iso] = {}
            # Percentage might be missing, default to 0
            try:
                p_val = float(perc) if perc else 0.0
            except:
                p_val = 0.0
            country_religions[iso][rel] = max(country_religions[iso].get(rel, 0.0), p_val)

    # 3. Law & Safety
    for r in results[2]:
        iso = r.get("countryISO", {}).get("value")
        if iso not in country_map: continue
        c = country_map[iso]
        if not c.alcohol_status: c.alcohol_status = r.get("alcoholLabel", {}).get("value")
        if not c.lgbtq_status: c.lgbtq_status = r.get("lgbtqLabel", {}).get("value")
        if not c.id_requirement: c.id_requirement = r.get("idReqLabel", {}).get("value")
        
        hazard = r.get("hazardLabel", {}).get("value")
        if hazard and not hazard.startswith("Q"):
            if iso not in country_hazards: country_hazards[iso] = set()
            country_hazards[iso].add(hazard)

    # 4. Transport
    for r in results[3]:
        iso = r.get("countryISO", {}).get("value")
        if iso not in country_map: continue
        c = country_map[iso]
        if not c.main_airport: c.main_airport = r.get("airportLabel", {}).get("value")
        if not c.railway_info: c.railway_info = r.get("railwayLabel", {}).get("value")

    # Apply Grouped Data & Fallbacks
    for iso, c in country_map.items():
        if iso in country_ethnics:
            c.ethnic_groups = ", ".join(sorted(list(country_ethnics[iso]))[:5])
        if iso in country_hazards:
            c.natural_hazards = ", ".join(sorted(list(country_hazards[iso]))[:5])
        
        # Apply religions
        rels = country_religions.get(iso, {})
        total_p = sum(rels.values())
        
        # Always update last_updated for religions even if using fallbacks
        db.query(models.Religion).filter(models.Religion.country_id == c.id).delete()
        
        if rels and total_p > 0:
            sorted_rels = sorted(rels.items(), key=lambda x: x[1], reverse=True)
            for name, p in sorted_rels[:5]:
                db.add(models.Religion(country_id=c.id, name=name, percentage=p))
        else:
            # Hardcoded fallbacks for major countries where Wikidata item is missing P140 or percentages
            fallbacks = {
                'PL': [("chrześcijaństwo", 92.0), ("brak wyznania", 6.0)],
                'AE': [("islam", 76.0), ("chrześcijaństwo", 9.0), ("hinduizm", 5.0)],
                'EG': [("islam", 90.0), ("chrześcijaństwo", 10.0)],
                'IT': [("chrześcijaństwo", 80.0), ("brak wyznania", 15.0)],
                'ES': [("chrześcijaństwo", 60.0), ("brak wyznania", 35.0)],
                'FR': [("chrześcijaństwo", 50.0), ("brak wyznania", 35.0), ("islam", 5.0)],
                'TR': [("islam", 99.0)],
                'MA': [("islam", 99.0)],
                'TN': [("islam", 99.0)],
                'ID': [("islam", 87.0), ("chrześcijaństwo", 10.0)],
                'TH': [("buddyzm", 94.0), ("islam", 5.0)]
            }
            if iso in fallbacks:
                for name, p in fallbacks[iso]:
                    db.add(models.Religion(country_id=c.id, name=name, percentage=p))
            elif rels: # Use what we found even if 0%
                for name, p in list(rels.items())[:5]:
                    db.add(models.Religion(country_id=c.id, name=name, percentage=p))

        # Fallbacks
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
                c.id_requirement = "Dowód osobisty lub Paszport" if iso in EU_EEA else "Paszport"
    
    db.commit()

async def sync_things_batch(db: Session, countries: list[models.Country]):
    if not countries: return
    country_map = {c.iso_alpha2.upper(): c for c in countries}
    isos = ' '.join([f'"{iso}"' for iso in country_map.keys()])
    
    query = f"SELECT DISTINCT ?countryISO ?thingLabel WHERE {{ VALUES ?countryISO {{ {isos} }} ?country wdt:P297 ?countryISO. ?thing wdt:P31/wdt:P279* wd:Q570116; wdt:P17 ?country. SERVICE wikibase:label {{ bd:serviceParam wikibase:language 'pl,en'. }} }}"
    
    data = await async_sparql_get(query, "Unique Things")
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
    batch_size = 5 # Smaller batches
    
    print(f"Syncing extended info in batches of {batch_size}...")
    for i in range(0, len(countries), batch_size):
        batch = countries[i : i + batch_size]
        print(f"Progress: {i}/{len(countries)} countries...")
        await sync_wikidata_batch(db, batch)
        await asyncio.sleep(1.0)
        await sync_things_batch(db, batch)
        await asyncio.sleep(2.0) # More delay between batches
    
    return {"status": "done"}

async def sync_wikidata_country_info(db: Session, country_iso2: str):
    country = db.query(models.Country).filter(models.Country.iso_alpha2 == country_iso2.upper()).first()
    if country:
        await sync_wikidata_batch(db, [country])
        await sync_things_batch(db, [country])
    return {"status": "done"}
