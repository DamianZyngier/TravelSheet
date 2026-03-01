import httpx
from sqlalchemy.orm import Session
from .. import models
import asyncio
import logging

logger = logging.getLogger("uvicorn")

async def sync_wikidata_country_info(db: Session, country_iso2: str):
    country = db.query(models.Country).filter(models.Country.iso_alpha2 == country_iso2.upper()).first()
    if not country: return {"error": "Country not found"}

    # SPARQL Query for basic info, phone code, ethnic groups, unique animals, and new law/transport fields
    query = f"""
    SELECT ?timezoneLabel ?dishLabel ?phoneCode ?ethnicLabel ?religionLabel ?religionPercent 
           ?animalLabel ?alcoholLabel ?lgbtqLabel ?idReqLabel ?airportLabel ?railwayLabel 
           ?hazardLabel WHERE {{
      ?country wdt:P297 "{country_iso2.upper()}".
      OPTIONAL {{ ?country wdt:P421 ?timezone. }}
      OPTIONAL {{ ?country wdt:P3646 ?dish. }}
      OPTIONAL {{ ?country wdt:P442 ?phoneCode. }}
      
      # Ethnic groups
      OPTIONAL {{ 
        ?country p:P172 [ ps:P172 ?ethnic; pq:P2107 ?ethnicPercent ]. 
      }}
      
      # Religions
      OPTIONAL {{
        ?country p:P140 [ ps:P140 ?religion; pq:P2107 ?religionPercent ].
      }}

      # Unique/National Animal
      OPTIONAL {{ ?country wdt:P2579 ?animal. }}
      
      # Law & Safety
      OPTIONAL {{ ?country wdt:P3931 ?alcohol. }}
      OPTIONAL {{ ?country wdt:P91 ?lgbtq. }}
      OPTIONAL {{ ?country wdt:P3120 ?idReq. }}
      
      # Transport
      OPTIONAL {{ ?country wdt:P114 ?airport. }}
      OPTIONAL {{ ?country wdt:P1194 ?railway. }}
      
      # Environment
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

    # Separate query for unique attractions or famous landmarks
    things_query = f"""
    SELECT ?thingLabel WHERE {{
      ?thing wdt:P31/wdt:P279* wd:Q570116;
             wdt:P17 ?country.
      ?country wdt:P297 "{country_iso2.upper()}".
      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "pl,en". }}
    }}
    LIMIT 10
    """

    # Separate query for largest cities (top 5 by population)
    cities_query = f"""
    SELECT ?cityLabel ?pop WHERE {{
      ?city wdt:P31 wd:Q515;
            wdt:P17 ?country;
            wdt:P1082 ?pop.
      ?country wdt:P297 "{country_iso2.upper()}".
      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "pl,en". }}
    }}
    ORDER BY DESC(?pop)
    LIMIT 5
    """

    url = "https://query.wikidata.org/sparql"
    headers = {
        "User-Agent": "TravelCheatsheet/1.0 (https://github.com/zyngi/TravelSheet)",
        "Accept": "application/sparql-results+json"
    }

    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            # 1. Main info
            resp = await client.get(url, params={'query': query}, headers=headers)
            if resp.status_code == 200:
                data = resp.json()
                bindings = data.get("results", {}).get("bindings", [])
                
                ethnics = set()
                animals = set()
                hazards = set()
                religions = {} # Use dict to store highest percentage per religion
                
                for r in bindings:
                    # Basic fields
                    if not country.timezone: country.timezone = r.get("timezoneLabel", {}).get("value")
                    if not country.national_dish: country.national_dish = r.get("dishLabel", {}).get("value")
                    if not country.phone_code: country.phone_code = r.get("phoneCode", {}).get("value")
                    
                    # New fields
                    if not country.alcohol_status: country.alcohol_status = r.get("alcoholLabel", {}).get("value")
                    if not country.lgbtq_status: country.lgbtq_status = r.get("lgbtqLabel", {}).get("value")
                    if not country.id_requirement: country.id_requirement = r.get("idReqLabel", {}).get("value")
                    if not country.main_airport: country.main_airport = r.get("airportLabel", {}).get("value")
                    if not country.railway_info: country.railway_info = r.get("railwayLabel", {}).get("value")

                    # Collections
                    ethnic = r.get("ethnicLabel", {}).get("value")
                    if ethnic: ethnics.add(ethnic)
                    
                    animal = r.get("animalLabel", {}).get("value")
                    if animal: animals.add(animal)

                    hazard = r.get("hazardLabel", {}).get("value")
                    if hazard: hazards.add(hazard)
                    
                    rel = r.get("religionLabel", {}).get("value")
                    perc = r.get("religionPercent", {}).get("value")
                    if rel and perc:
                        religions[rel] = max(religions.get(rel, 0), float(perc))

                if ethnics: country.ethnic_groups = ", ".join(list(ethnics)[:5])
                if animals: country.unique_animals = ", ".join(list(animals)[:5])
                if hazards: country.natural_hazards = ", ".join(list(hazards)[:5])
                
                # Communication (regional defaults as Wiki doesn't have a direct "popular social media" property often)
                if not country.popular_apps:
                    if country.continent == 'Europe': country.popular_apps = "WhatsApp, Messenger, Instagram"
                    elif country.continent == 'Asia': country.popular_apps = "WhatsApp, WeChat, Line, Telegram"
                    elif country.continent == 'Americas': country.popular_apps = "WhatsApp, Messenger, Instagram"
                    elif country.continent == 'Africa': country.popular_apps = "WhatsApp, Facebook"
                    else: country.popular_apps = "WhatsApp, Messenger"
                
                # Update Religions in DB
                if religions:
                    db.query(models.Religion).filter(models.Religion.country_id == country.id).delete()
                    for name, p in religions.items():
                        db.add(models.Religion(country_id=country.id, name=name, percentage=p))

            # 2. Things/Unique
            resp_things = await client.get(url, params={'query': things_query}, headers=headers)
            if resp_things.status_code == 200:
                thing_data = resp_things.json().get("results", {}).get("bindings", [])
                things = [f"{c['thingLabel']['value']}" for c in thing_data]
                if things: country.unique_things = ", ".join(things[:5])

            # 3. Cities
            resp_cities = await client.get(url, params={'query': cities_query}, headers=headers)
            if resp_cities.status_code == 200:
                city_data = resp_cities.json().get("results", {}).get("bindings", [])
                cities = [f"{c['cityLabel']['value']}" for c in city_data]
                if cities: country.largest_cities = ", ".join(cities)

            db.commit()
            return {"status": "success"}
        except Exception as e:
            logger.error(f"Wikidata error: {e}")
            return {"error": str(e)}

async def sync_all_wikidata_info(db: Session):
    countries = db.query(models.Country).all()
    for c in countries:
        await sync_wikidata_country_info(db, c.iso_alpha2)
        await asyncio.sleep(0.5)
    return {"status": "done"}
