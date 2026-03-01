import httpx
from sqlalchemy.orm import Session
from .. import models
import asyncio
import logging

logger = logging.getLogger("uvicorn")
# Wyciszenie logów HTTPX
logging.getLogger("httpx").setLevel(logging.WARNING)

async def sync_wikidata_country_info(db: Session, country_iso2: str):
    country = db.query(models.Country).filter(models.Country.iso_alpha2 == country_iso2.upper()).first()
    if not country: return {"error": "Country not found"}

    # SPARQL Query for basic info, phone code, ethnic groups, unique animals, and new law/transport fields
    # Removed comments from query string to avoid interpolation issues
    query = f"""
    SELECT ?timezoneLabel ?dishLabel ?phoneCode ?ethnicLabel ?religionLabel ?religionPercent 
           ?animalLabel ?alcoholLabel ?lgbtqLabel ?idReqLabel ?airportLabel ?railwayLabel 
           ?hazardLabel WHERE {{
      ?country wdt:P297 "{country_iso2.upper()}".
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

    things_query = f"""
    SELECT DISTINCT ?thingLabel WHERE {{
      ?thing wdt:P31/wdt:P279* wd:Q570116;
             wdt:P17 ?country.
      ?country wdt:P297 "{country_iso2.upper()}".
      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "pl,en". }}
    }}
    LIMIT 20
    """

    cities_query = f"""
    SELECT DISTINCT ?cityLabel ?pop WHERE {{
      ?city wdt:P31 wd:Q515;
            wdt:P17 ?country;
            wdt:P1082 ?pop.
      ?country wdt:P297 "{country_iso2.upper()}".
      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "pl,en". }}
    }}
    ORDER BY DESC(?pop)
    LIMIT 10
    """

    url = "https://query.wikidata.org/sparql"
    headers = {
        "User-Agent": "TravelCheatsheet/1.0 (https://github.com/zyngi/TravelSheet)",
        "Accept": "application/sparql-results+json",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            # Use POST for SPARQL to avoid URL truncation and issues with large queries
            # 1. Main info
            resp = await client.post(url, data={'query': query}, headers=headers)
            if resp.status_code == 200:
                data = resp.json()
                bindings = data.get("results", {}).get("bindings", [])
                
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
                
                if not country.popular_apps:
                    if country.continent == 'Europe': country.popular_apps = "WhatsApp, Messenger, Instagram"
                    elif country.continent == 'Asia': country.popular_apps = "WhatsApp, WeChat, Line, Telegram"
                    elif country.continent == 'Americas': country.popular_apps = "WhatsApp, Messenger, Instagram"
                    elif country.continent == 'Africa': country.popular_apps = "WhatsApp, Facebook"
                    else: country.popular_apps = "WhatsApp, Messenger"
                
                if religions:
                    db.query(models.Religion).filter(models.Religion.country_id == country.id).delete()
                    for name, p in religions.items():
                        db.add(models.Religion(country_id=country.id, name=name, percentage=p))

            # 2. Things/Unique
            resp_things = await client.post(url, data={'query': things_query}, headers=headers)
            if resp_things.status_code == 200:
                thing_data = resp_things.json().get("results", {}).get("bindings", [])
                # Use set to avoid duplicates
                things = set()
                for c in thing_data:
                    val = c['thingLabel']['value']
                    if val and not val.startswith("Q"):
                        things.add(val)
                if things: country.unique_things = ", ".join(sorted(list(things))[:5])

            # 3. Cities
            resp_cities = await client.post(url, data={'query': cities_query}, headers=headers)
            if resp_cities.status_code == 200:
                city_data = resp_cities.json().get("results", {}).get("bindings", [])
                cities = set()
                for c in city_data:
                    val = c['cityLabel']['value']
                    if val and not val.startswith("Q"):
                        cities.add(val)
                if cities: country.largest_cities = ", ".join(sorted(list(cities))[:5])

            db.commit()
            return {"status": "success"}
        except Exception as e:
            logger.error(f"Wikidata error for {country_iso2}: {e}")
            return {"error": str(e)}

async def sync_all_wikidata_info(db: Session):
    countries = db.query(models.Country).all()
    logger.info(f"Syncing extended Wikidata info for {len(countries)} countries...")
    for i, c in enumerate(countries):
        await sync_wikidata_country_info(db, c.iso_alpha2)
        if (i+1) % 20 == 0:
            logger.info(f"Progress: {i+1}/{len(countries)} countries...")
        await asyncio.sleep(0.6) # Slightly more delay to be safe
    return {"status": "done"}
