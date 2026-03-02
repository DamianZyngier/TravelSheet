import httpx
from sqlalchemy.orm import Session
from .. import models
import asyncio
import logging
from .utils import async_sparql_get

logger = logging.getLogger("uvicorn")
logging.getLogger("httpx").setLevel(logging.WARNING)

def format_pop(pop):
    if pop >= 1000000: return f"{pop/1000000:.1f} mln"
    if pop >= 1000: return f"{pop/1000:.0f} tys."
    return str(pop)

async def sync_wikidata_batch(db: Session, countries: list[models.Country]):
    """Sync info using multiple small queries for speed and stability"""
    if not countries: return
    country_map = {c.iso_alpha2.upper(): c for c in countries}
    isos = ' '.join([f'"{iso}"' for iso in country_map.keys()])
    
    # Query 1: Simple Info
    q_simple = f"SELECT ?countryISO ?timezoneLabel ?dishLabel ?phoneCode WHERE {{ VALUES ?countryISO {{ {isos} }} ?country wdt:P297 ?countryISO. OPTIONAL {{ ?country wdt:P421 ?timezone. }} OPTIONAL {{ ?country wdt:P3646 ?dish. }} OPTIONAL {{ ?country wdt:P442 ?phoneCode. }} SERVICE wikibase:label {{ bd:serviceParam wikibase:language 'pl,en'. }} }}"
    
    # Query 2: Cultural (Ethnics & Religions)
    q_cultural = f"SELECT ?countryISO ?ethnicLabel ?religionLabel ?religionPercent WHERE {{ VALUES ?countryISO {{ {isos} }} ?country wdt:P297 ?countryISO. OPTIONAL {{ ?country p:P172 [ ps:P172 ?ethnic; pq:P2107 ?ethnicPercent ]. }} OPTIONAL {{ ?country p:P140 ?relStatement. ?relStatement ps:P140 ?religion. OPTIONAL {{ ?relStatement pq:P2107 ?religionPercent. }} }} SERVICE wikibase:label {{ bd:serviceParam wikibase:language 'pl,en'. }} }}"
    
    # Query 3: Law & Safety
    q_law = f"SELECT ?countryISO ?animalLabel ?alcoholLabel ?lgbtqLabel ?idReqLabel ?hazardLabel WHERE {{ VALUES ?countryISO {{ {isos} }} ?country wdt:P297 ?countryISO. OPTIONAL {{ ?country wdt:P1584 ?animal. }} OPTIONAL {{ ?country wdt:P3931 ?alcohol. }} OPTIONAL {{ ?country wdt:P91 ?lgbtq. }} OPTIONAL {{ ?country wdt:P3120 ?idReq. }} OPTIONAL {{ ?country wdt:P1057 ?hazard. }} SERVICE wikibase:label {{ bd:serviceParam wikibase:language 'pl,en'. }} }}"

    # Query 4: Transport
    q_trans = f"SELECT ?countryISO ?airportLabel ?railwayLabel WHERE {{ VALUES ?countryISO {{ {isos} }} ?country wdt:P297 ?countryISO. OPTIONAL {{ ?country wdt:P114 ?airport. }} OPTIONAL {{ ?country wdt:P1194 ?railway. }} SERVICE wikibase:label {{ bd:serviceParam wikibase:language 'pl,en'. }} }}"

    # Query 5: Largest Cities with Population
    q_cities = f"""
    SELECT ?countryISO ?cityLabel ?pop WHERE {{
      VALUES ?countryISO {{ {isos} }}
      ?country wdt:P297 ?countryISO.
      ?city wdt:P31/wdt:P279* wd:Q515;
            wdt:P17 ?country;
            wdt:P1082 ?pop.
      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "pl,en". }}
    }}
    ORDER BY DESC(?pop)
    """

    # Run queries sequential
    results = [
        await async_sparql_get(q_simple, "Simple Info"),
        await async_sparql_get(q_cultural, "Cultural Info"),
        await async_sparql_get(q_law, "Law Info"),
        await async_sparql_get(q_trans, "Transport Info"),
        await async_sparql_get(q_cities, "Cities Info")
    ]
    
    country_religions = {} 
    country_ethnics = {} 
    country_hazards = {} 
    country_cities = {} 

    # Process results (Simple, Cultural, Law, Trans same as before)
    for r in results[0]:
        iso = r.get("countryISO", {}).get("value")
        if iso in country_map:
            c = country_map[iso]
            if not c.timezone: c.timezone = r.get("timezoneLabel", {}).get("value")
            if not c.national_dish: c.national_dish = r.get("dishLabel", {}).get("value")
            if not c.phone_code: c.phone_code = r.get("phoneCode", {}).get("value")
    
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
            try: p_val = float(perc) if perc else 0.0
            except: p_val = 0.0
            country_religions[iso][rel] = max(country_religions[iso].get(rel, 0.0), p_val)

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

    for r in results[3]:
        iso = r.get("countryISO", {}).get("value")
        if iso not in country_map: continue
        c = country_map[iso]
        if not c.main_airport: c.main_airport = r.get("airportLabel", {}).get("value")
        if not c.railway_info: c.railway_info = r.get("railwayLabel", {}).get("value")

    for r in results[4]:
        iso = r.get("countryISO", {}).get("value")
        name = r.get("cityLabel", {}).get("value")
        pop = r.get("pop", {}).get("value")
        if iso and name and pop and not name.startswith("Q"):
            if iso not in country_cities: country_cities[iso] = []
            if len(country_cities[iso]) < 5:
                try: country_cities[iso].append((name, int(float(pop))))
                except: continue

    # Apply data with fallbacks for cities
    city_fallbacks = {
        'PL': [("Warszawa", 1860000), ("Kraków", 800000), ("Wrocław", 670000), ("Łódź", 660000), ("Poznań", 540000)],
        'US': [("Nowy Jork", 8300000), ("Los Angeles", 3800000), ("Chicago", 2600000), ("Houston", 2300000), ("Phoenix", 1600000)],
        'DE': [("Berlin", 3700000), ("Hamburg", 1900000), ("Monachium", 1500000), ("Kolonia", 1100000), ("Frankfurt", 760000)],
        'FR': [("Paryż", 2100000), ("Marsylia", 870000), ("Lyon", 520000), ("Tuluza", 490000), ("Nicea", 340000)],
        'GB': [("Londyn", 8900000), ("Birmingham", 1100000), ("Glasgow", 630000), ("Liverpool", 500000), ("Leeds", 480000)],
        'IT': [("Rzym", 2800000), ("Mediolan", 1400000), ("Neapol", 960000), ("Turyn", 870000), ("Palermo", 660000)],
        'ES': [("Madryt", 3300000), ("Barcelona", 1600000), ("Walencja", 790000), ("Sewilla", 680000), ("Zaragoza", 670000)],
        'JP': [("Tokio", 14000000), ("Jokohama", 3700000), ("Osaka", 2700000), ("Nagoja", 2300000), ("Sapporo", 2200000)],
        'BR': [("São Paulo", 12300000), ("Rio de Janeiro", 6700000), ("Brasília", 3000000), ("Salvador", 2900000), ("Fortaleza", 2700000)],
        'AE': [("Dubaj", 3300000), ("Abu Zabi", 1500000), ("Szardża", 1300000), ("Al-Ajn", 760000), ("Adżman", 490000)],
        'EG': [("Kair", 10000000), ("Giza", 9000000), ("Aleksandria", 5200000), ("Szubra al-Chajma", 1200000), ("Mansura", 620000)],
        'TH': [("Bangkok", 10500000), ("Nonthaburi", 250000), ("Pak Kret", 190000), ("Hat Yai", 160000), ("Nakhon Ratchasima", 130000)],
        'TR': [("Stambuł", 15500000), ("Ankara", 5700000), ("Izmir", 4400000), ("Bursa", 3100000), ("Adana", 2200000)],
        'ID': [("Dżakarta", 10500000), ("Surabaja", 2900000), ("Bekasi", 2500000), ("Bandung", 2400000), ("Medan", 2200000)],
        'AU': [("Sydney", 5300000), ("Melbourne", 5000000), ("Brisbane", 2500000), ("Perth", 2100000), ("Adelaide", 1300000)]
    }

    for iso, c in country_map.items():
        if iso in country_ethnics: c.ethnic_groups = ", ".join(sorted(list(country_ethnics[iso]))[:5])
        if iso in country_hazards: c.natural_hazards = ", ".join(sorted(list(country_hazards[iso]))[:5])
        
        # Cities
        cities = country_cities.get(iso, [])
        if not cities and iso in city_fallbacks: cities = city_fallbacks[iso]
        
        if cities:
            # Final sorting by pop desc just in case
            cities.sort(key=lambda x: x[1], reverse=True)
            c.largest_cities = ", ".join([f"{name} ({format_pop(pop)})" for name, pop in cities])
        
        # Religions (existing)
        rels = country_religions.get(iso, {})
        db.query(models.Religion).filter(models.Religion.country_id == c.id).delete()
        if rels and sum(rels.values()) > 0:
            sorted_rels = sorted(rels.items(), key=lambda x: x[1], reverse=True)
            for name, p in sorted_rels[:5]:
                db.add(models.Religion(country_id=c.id, name=name, percentage=p))
        else:
            rel_fallbacks = {
                'PL': [("chrześcijaństwo", 92.0), ("brak wyznania", 6.0)],
                'AE': [("islam", 76.0), ("chrześcijaństwo", 9.0), ("hinduizm", 5.0)],
                'EG': [("islam", 90.0), ("chrześcijaństwo", 10.0)],
                'IT': [("chrześcijaństwo", 80.0), ("brak wyznania", 15.0)],
                'ES': [("chrześcijaństwo", 60.0), ("brak wyznania", 35.0)],
                'FR': [("chrześcijaństwo", 50.0), ("brak wyznania", 35.0), ("islam", 5.0)],
                'TR': [("islam", 99.0)], 'MA': [("islam", 99.0)], 'TN': [("islam", 99.0)],
                'ID': [("islam", 87.0), ("chrześcijaństwo", 10.0)], 'TH': [("buddyzm", 94.0), ("islam", 5.0)]
            }
            if iso in rel_fallbacks:
                for name, p in rel_fallbacks[iso]:
                    db.add(models.Religion(country_id=c.id, name=name, percentage=p))
    
    db.commit()

async def sync_things_batch(db: Session, countries: list[models.Country]):
    if not countries: return
    country_map = {c.iso_alpha2.upper(): c for c in countries}
    isos = ' '.join([f'"{iso}"' for iso in country_map.keys()])
    query = f"SELECT DISTINCT ?countryISO ?thingLabel WHERE {{ VALUES ?countryISO {{ {isos} }} ?country wdt:P297 ?countryISO. ?thing wdt:P31/wdt:P279* wd:Q570116; wdt:P17 ?country. SERVICE wikibase:label {{ bd:serviceParam wikibase:language 'pl,en'. }} }}"
    data = await async_sparql_get(query, "Unique Things")
    iso_things = {}
    for r in data:
        iso = r.get("countryISO", {}).get("value"); val = r.get("thingLabel", {}).get("value")
        if iso and val and not val.startswith("Q"):
            if iso not in iso_things: iso_things[iso] = set()
            iso_things[iso].add(val)
    for iso, things in iso_things.items():
        if iso in country_map: country_map[iso].unique_things = ", ".join(sorted(list(things))[:5])
    db.commit()

async def sync_all_wikidata_info(db: Session):
    countries = db.query(models.Country).all()
    batch_size = 5
    print(f"Syncing extended info in batches of {batch_size}...")
    for i in range(0, len(countries), batch_size):
        batch = countries[i : i + batch_size]
        print(f"Progress: {i}/{len(countries)} countries...")
        await sync_wikidata_batch(db, batch)
        await asyncio.sleep(1.0)
        await sync_things_batch(db, batch)
        await asyncio.sleep(2.0)
    return {"status": "done"}

async def sync_wikidata_country_info(db: Session, country_iso2: str):
    country = db.query(models.Country).filter(models.Country.iso_alpha2 == country_iso2.upper()).first()
    if country:
        await sync_wikidata_batch(db, [country])
        await sync_things_batch(db, [country])
    return {"status": "done"}
