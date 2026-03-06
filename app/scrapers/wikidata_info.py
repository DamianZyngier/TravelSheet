import httpx
from sqlalchemy.orm import Session
from .. import models
import asyncio
import logging
from .utils import async_sparql_get

logger = logging.getLogger("uvicorn")
logging.getLogger("httpx").setLevel(logging.WARNING)

def format_pop(pop):
    try:
        p = float(pop)
        if p >= 1000000: return f"{p/1000000:.1f} mln"
        if p >= 1000: return f"{p/1000:.0f} tys."
        return str(int(p))
    except:
        return str(pop)

async def sync_wikidata_batch(db: Session, countries: list[models.Country]):
    """Sync info using multiple small queries for speed and stability"""
    if not countries: return
    country_map = {c.iso_alpha2.upper(): c for c in countries}
    isos = ' '.join([f'"{iso}"' for iso in country_map.keys()])
    
    # Query 1: Basic & Advanced Stats (Timezone, Dish, Phone, Airport, Railway, Climate, HDI, Life Exp, GDP, Gini, Coat, Inception, Website)
    q_basic = f"""
    SELECT ?countryISO ?timezoneLabel ?dishLabel ?phoneCode ?airportLabel ?railwayLabel ?climateLabel 
           ?hdi ?lifeExp ?gdpNominal ?gdpPPP ?gini ?coatOfArms ?inception ?website WHERE {{
      VALUES ?countryISO {{ {isos} }}
      ?country wdt:P297 ?countryISO.
      OPTIONAL {{ ?country wdt:P421 ?timezone. }}
      OPTIONAL {{ ?country wdt:P3646 ?dish. }}
      OPTIONAL {{ ?country wdt:P442 ?phoneCode. }}
      OPTIONAL {{ ?country wdt:P114 ?airport. }}
      OPTIONAL {{ ?country wdt:P1194 ?railway. }}
      OPTIONAL {{ ?country wdt:P2524 ?climate. }}
      OPTIONAL {{ ?country wdt:P1081 ?hdi. }}
      OPTIONAL {{ ?country wdt:P2250 ?lifeExp. }}
      OPTIONAL {{ ?country wdt:P2131 ?gdpNominal. }}
      OPTIONAL {{ ?country wdt:P2132 ?gdpPPP. }}
      OPTIONAL {{ ?country wdt:P3529 ?gini. }}
      OPTIONAL {{ ?country wdt:P94 ?coatOfArms. }}
      OPTIONAL {{ ?country wdt:P571 ?inception. }}
      OPTIONAL {{ ?country wdt:P856 ?website. }}
      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "pl,en". }}
    }}
    """
    
    # Query 2: Cultural (Ethnics & Religions)
    q_cultural = f"""
    SELECT ?countryISO ?ethnicLabel ?religionLabel ?religionPercent WHERE {{
      VALUES ?countryISO {{ {isos} }}
      ?country wdt:P297 ?countryISO.
      OPTIONAL {{ ?country p:P172 [ ps:P172 ?ethnic; pq:P2107 ?ethnicPercent ]. }}
      OPTIONAL {{ 
        ?country p:P140 ?relStatement.
        ?relStatement ps:P140 ?religion.
        OPTIONAL {{ ?relStatement pq:P2107 ?religionPercent. }}
      }}
      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "pl,en". }}
    }}
    """
    
    # Query 3: Law & Safety
    q_law = f"""
    SELECT ?countryISO ?alcoholLabel ?lgbtqLabel ?idReqLabel ?hazardLabel WHERE {{
      VALUES ?countryISO {{ {isos} }}
      ?country wdt:P297 ?countryISO.
      OPTIONAL {{ ?country wdt:P3931 ?alcohol. }}
      OPTIONAL {{ ?country wdt:P91 ?lgbtq. }}
      OPTIONAL {{ ?country wdt:P3120 ?idReq. }}
      OPTIONAL {{ ?country wdt:P1057 ?hazard. }}
      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "pl,en". }}
    }}
    """

    # Query 4: Largest Cities
    q_cities = f"""
    SELECT ?countryISO ?cityLabel ?pop WHERE {{
      VALUES ?countryISO {{ {isos} }}
      ?country wdt:P297 ?countryISO.
      ?city wdt:P31/wdt:P279* wd:Q515; wdt:P17 ?country.
      OPTIONAL {{ ?city wdt:P1082 ?pop. }}
      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "pl,en". }}
    }}
    """

    # Query 5: Souvenirs / Local Products (Handicrafts, Specialties, GIs)
    q_products = f"""
    SELECT ?countryISO ?itemLabel WHERE {{
      VALUES ?countryISO {{ {isos} }}
      ?country wdt:P297 ?countryISO.
      {{
        ?item wdt:P495 ?country.
        ?item wdt:P31/wdt:P279* ?type.
        VALUES ?type {{ wd:Q170658 wd:Q11690 wd:Q2095 wd:Q13182 wd:Q202816 }}
      }} UNION {{
        ?item wdt:P17 ?country.
        ?item wdt:P31/wdt:P279* wd:Q202816.
      }}
      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "pl,en". }}
    }}
    LIMIT 100
    """

    results = [
        await async_sparql_get(q_basic, "Basic & Advanced Stats"),
        await async_sparql_get(q_cultural, "Cultural Info"),
        await async_sparql_get(q_law, "Law Info"),
        await async_sparql_get(q_cities, "Cities Info"),
        await async_sparql_get(q_products, "Products/Souvenirs/GIs")
    ]
    
    country_religions = {} 
    country_ethnics = {} 
    country_hazards = {} 
    country_cities = {} 
    country_climates = {}
    country_souvenirs = {}

    # 1. Basic Stats
    for r in results[0]:
        iso = r.get("countryISO", {}).get("value")
        if iso not in country_map: continue
        c = country_map[iso]
        if not c.timezone: c.timezone = r.get("timezoneLabel", {}).get("value")
        if not c.national_dish: c.national_dish = r.get("dishLabel", {}).get("value")
        if not c.phone_code: c.phone_code = r.get("phoneCode", {}).get("value")
        if not c.main_airport: c.main_airport = r.get("airportLabel", {}).get("value")
        if not c.railway_info: c.railway_info = r.get("railwayLabel", {}).get("value")
        
        # New Advanced Fields
        if not c.hdi: 
            val = r.get("hdi", {}).get("value")
            if val: c.hdi = float(val)
        if not c.life_expectancy: 
            val = r.get("lifeExp", {}).get("value")
            if val: c.life_expectancy = float(val)
        if not c.gdp_nominal: 
            val = r.get("gdpNominal", {}).get("value")
            if val: c.gdp_nominal = float(val)
        if not c.gdp_ppp: 
            val = r.get("gdpPPP", {}).get("value")
            if val: c.gdp_ppp = float(val)
        if not c.gini: 
            val = r.get("gini", {}).get("value")
            if val: c.gini = float(val)
        if not c.coat_of_arms_url: c.coat_of_arms_url = r.get("coatOfArms", {}).get("value")
        if not c.inception_date: 
            inc = r.get("inception", {}).get("value")
            if inc: c.inception_date = inc.split('T')[0]
        if not c.official_tourist_website: c.official_tourist_website = r.get("website", {}).get("value")

        clim = r.get("climateLabel", {}).get("value")
        if clim and not clim.startswith("Q"):
            if iso not in country_climates: country_climates[iso] = set()
            country_climates[iso].add(clim)
    
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
            try: p_val = float(perc) if perc else 0.0
            except: p_val = 0.0
            country_religions[iso][rel] = max(country_religions[iso].get(rel, 0.0), p_val)

    # 3. Law
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

    # 4. Cities
    for r in results[3]:
        iso = r.get("countryISO", {}).get("value")
        name = r.get("cityLabel", {}).get("value")
        pop_val = r.get("pop", {}).get("value")
        
        if iso and name and not name.startswith("Q"):
            if iso not in country_cities: country_cities[iso] = []
            
            try: 
                pop = int(float(pop_val)) if pop_val else 0
            except: 
                pop = 0
                
            # Avoid duplicates (e.g. "Madrid" and "Madrid city")
            is_dup = False
            for i, (existing_name, existing_pop) in enumerate(country_cities[iso]):
                if name.lower() == existing_name.lower() or name.lower().startswith(existing_name.lower()) or existing_name.lower().startswith(name.lower()):
                    if pop > existing_pop:
                        country_cities[iso][i] = (name, pop)
                    is_dup = True
                    break
            
            if not is_dup:
                country_cities[iso].append((name, pop))

    # 5. Souvenirs
    for r in results[4]:
        iso = r.get("countryISO", {}).get("value")
        prod = r.get("itemLabel", {}).get("value")
        if iso and prod and not prod.startswith("Q"):
            if iso not in country_souvenirs: country_souvenirs[iso] = set()
            country_souvenirs[iso].add(prod)

    # Fallbacks and final application
    EXTRA_FALLBACKS = {
        'PL': {
            'dish': 'Bigos, Pierogi', 'climate': 'Klimat umiarkowany przejściowy',
            'souvenirs': 'Bursztyn, Ceramika bolesławiecka, Wyroby z lnu, Krówki, Oscypek'
        },
        'EG': {
            'climate': 'Klimat zwrotnikowy suchy (pustynny)',
            'souvenirs': 'Papirusy, Olejki zapachowe, Przyprawy, Wyroby z alabastru, Bawełna egipska'
        },
        'TH': {
            'climate': 'Klimat zwrotnikowy monsunowy',
            'souvenirs': 'Jedwab tajski, Wyroby z drewna tekowego, Naturalne kosmetyki, Figurki słoni, Produkty kokosowe'
        },
        'MX': {
            'climate': 'Zróżnicowany: zwrotnikowy suchy na północy, wilgotny na południu',
            'souvenirs': 'Tequila, Mezcal, Ceramika Talavera, Wyroby ze srebra, Kapelusze Sombrero'
        },
        'FR': {
            'climate': 'Klimat umiarkowany morski, na południu śródziemnomorski',
            'souvenirs': 'Wina, Sery, Perfumy, Makaroniki, Berety, Wyroby z lawendy (Prowansja)'
        },
        'IT': {
            'climate': 'Klimat śródziemnomorski',
            'souvenirs': 'Wyroby skórzane, Oliwa z oliwek, Ocet balsamiczny, Szkło weneckie (Murano), Ceramika'
        },
        'ES': {
            'climate': 'Klimat śródziemnomorski i kontynentalny',
            'souvenirs': 'Wachlarze, Wyroby ze skóry, Oliwa, Szafran, Ceramika, Espadryle'
        },
        'GR': {
            'climate': 'Klimat śródziemnomorski',
            'souvenirs': 'Oliwa z oliwek, Naturalne gąbki, Miód tymiankowy, Ouzo, Biżuteria antyczna'
        },
        'TR': {
            'souvenirs': 'Dywaniki, Turecka herbata i kawa, Chałwa, Oko proroka (Nazar), Wyroby ze skóry'
        },
        'JP': {
            'souvenirs': 'Pałeczki, Matcha, Ceramika, Kimono/Yukata, Wyroby z papieru Washi, Noże kuchenne'
        }
    }

    for iso, c in country_map.items():
        fallback = EXTRA_FALLBACKS.get(iso)
        if fallback:
            if not c.national_dish and 'dish' in fallback: c.national_dish = fallback['dish']
            if not c.climate_description and 'climate' in fallback: c.climate_description = fallback['climate']
            if fallback.get('souvenirs'):
                c.practical.souvenirs = fallback['souvenirs']

        if iso in country_climates and not c.climate_description:
            c.climate_description = ", ".join(sorted(list(country_climates[iso]))[:3])

        if not c.practical.souvenirs and iso in country_souvenirs:
            s_list = [s for s in country_souvenirs[iso] if len(s) > 2][:6]
            c.practical.souvenirs = ", ".join(s_list)

        if iso in country_ethnics: c.ethnic_groups = ", ".join(sorted(list(country_ethnics[iso]))[:5])
        if iso in country_hazards: c.natural_hazards = ", ".join(sorted(list(country_hazards[iso]))[:5])
        
        cities = country_cities.get(iso, [])
        if cities:
            cities.sort(key=lambda x: x[1], reverse=True)
            c.largest_cities = ", ".join([f"{name} ({format_pop(pop)})" for name, pop in cities])
        
        # Religions
        rels = country_religions.get(iso, {})
        db.query(models.Religion).filter(models.Religion.country_id == c.id).delete()
        if rels:
            # If we have some data but all percentages are 0, assign a small value to top 3 
            # so they show up as "Major religion" in the UI logic.
            total_perc = sum(rels.values())
            sorted_rels = sorted(rels.items(), key=lambda x: x[1], reverse=True)
            
            if total_perc == 0 and sorted_rels:
                # No percentage data but we found religions - assign 0 to indicate "Presence known, percent unknown"
                for name, p in sorted_rels[:5]:
                    db.add(models.Religion(country_id=c.id, name=name, percentage=0.0))
            else:
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
    
    # Improved query with sitelinks filter to prioritize famous things and avoid timeouts
    query = f"""
    SELECT DISTINCT ?countryISO ?thingLabel WHERE {{ 
      VALUES ?countryISO {{ {isos} }} 
      ?country wdt:P297 ?countryISO. 
      ?thing wdt:P31/wdt:P279* wd:Q570116; 
             wdt:P17 ?country;
             wikibase:sitelinks ?sitelinks.
      FILTER(?sitelinks > 10)
      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "pl,en". }} 
    }}
    LIMIT 100
    """
    data = await async_sparql_get(query, "Unique Things")
    iso_things = {}
    for r in data:
        iso = r.get("countryISO", {}).get("value"); val = r.get("thingLabel", {}).get("value")
        if iso and val and not val.startswith("Q"):
            if iso not in iso_things: iso_things[iso] = set()
            iso_things[iso].add(val)
    for iso, things in iso_things.items():
        if iso in country_map: 
            country_map[iso].unique_things = ", ".join(sorted(list(things))[:5])
    db.commit()

async def sync_all_wikidata_info(db: Session):
    countries = db.query(models.Country).all()
    batch_size = 5
    results = {"success": 0, "errors": 0}
    print(f"Syncing extended info in batches of {batch_size}...")
    for i in range(0, len(countries), batch_size):
        batch = countries[i : i + batch_size]
        print(f"Progress: {i}/{len(countries)} countries...")
        try:
            await sync_wikidata_batch(db, batch)
            await asyncio.sleep(0.5)
            await sync_things_batch(db, batch)
            results["success"] += len(batch)
        except Exception as e:
            logger.error(f"Error in wikidata batch: {e}")
            results["errors"] += len(batch)
        await asyncio.sleep(1.0)
    return results

async def sync_wikidata_country_info(db: Session, country_iso2: str):
    country = db.query(models.Country).filter(models.Country.iso_alpha2 == country_iso2.upper()).first()
    if country:
        await sync_wikidata_batch(db, [country])
        await sync_things_batch(db, [country])
    return {"status": "done"}
