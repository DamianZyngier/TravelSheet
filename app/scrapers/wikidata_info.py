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
    
    # 1. Fast Batch Query: Basic & Advanced Stats (1-to-1 relations)
    q_stats = f"""
    SELECT ?countryISO ?timezoneLabel ?dishLabel ?phoneCode ?airportLabel ?railwayLabel ?climateLabel 
           ?hdi ?lifeExp ?gdpNominal ?gdpPPP ?gdpCapita ?gini ?coatOfArms ?inception ?website WHERE {{
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
      OPTIONAL {{ ?country wdt:P2127 ?gdpCapita. }}
      OPTIONAL {{ ?country wdt:P3529 ?gini. }}
      OPTIONAL {{ ?country wdt:P94 ?coatOfArms. }}
      OPTIONAL {{ ?country wdt:P571 ?inception. }}
      OPTIONAL {{ ?country wdt:P856 ?website. }}
      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "pl,en". }}
    }}
    """
    
    stats_results = await async_sparql_get(q_stats, "Basic & Advanced Stats")
    
    country_climates = {}
    for r in stats_results:
        iso = r.get("countryISO", {}).get("value")
        if iso not in country_map: continue
        c = country_map[iso]
        if not c.timezone: c.timezone = r.get("timezoneLabel", {}).get("value")
        if not c.national_dish: c.national_dish = r.get("dishLabel", {}).get("value")
        if not c.phone_code: c.phone_code = r.get("phoneCode", {}).get("value")
        if not c.main_airport: c.main_airport = r.get("airportLabel", {}).get("value")
        if not c.railway_info: c.railway_info = r.get("railwayLabel", {}).get("value")
        
        # Numeric Stats
        try:
            if r.get("hdi"): c.hdi = float(r["hdi"]["value"])
            if r.get("lifeExp"): c.life_expectancy = float(r["lifeExp"]["value"])
            if r.get("gdpNominal"): c.gdp_nominal = float(r["gdpNominal"]["value"])
            if r.get("gdpPPP"): c.gdp_ppp = float(r["gdpPPP"]["value"])
            if r.get("gdpCapita"): 
                c.gdp_per_capita = float(r["gdpCapita"]["value"])
            elif c.gdp_nominal and c.population:
                c.gdp_per_capita = float(c.gdp_nominal) / float(c.population)
            if r.get("gini"): c.gini = float(r["gini"]["value"])
        except (ValueError, KeyError):
            pass

        if r.get("coatOfArms"): c.coat_of_arms_url = r["coatOfArms"]["value"]
        if r.get("inception"): c.inception_date = r["inception"]["value"].split('T')[0]
        if r.get("website"): c.official_tourist_website = r["website"]["value"]

        clim = r.get("climateLabel", {}).get("value")
        if clim and not clim.startswith("Q"):
            if iso not in country_climates: country_climates[iso] = set()
            country_climates[iso].add(clim)

    # 2. Detailed Info - processed per country to avoid complex 504 timeouts
    for iso, c in country_map.items():
        # Cities: Top 10 by population
        q_cities = f"""
        SELECT ?cityLabel ?pop WHERE {{
          ?country wdt:P297 "{iso}".
          ?city wdt:P31/wdt:P279* wd:Q515; wdt:P17 ?country; wdt:P1082 ?pop.
          SERVICE wikibase:label {{ bd:serviceParam wikibase:language "pl,en". }}
        }}
        ORDER BY DESC(?pop)
        LIMIT 15
        """
        city_data = await async_sparql_get(q_cities, f"Cities for {iso}")
        cities = []
        seen_names = set()
        for r in city_data:
            name = r.get("cityLabel", {}).get("value")
            pop_val = r.get("pop", {}).get("value")
            if name and pop_val and name not in seen_names and not name.startswith("Q"):
                cities.append((name, int(float(pop_val))))
                seen_names.add(name)
        
        if cities:
            cities.sort(key=lambda x: x[1], reverse=True)
            max_pop = cities[0][1]
            # Limit to top 10, but only those with at least 10% of the largest city's population
            filtered_cities = [city for city in cities[:10] if city[1] >= max_pop * 0.1]
            # Ensure we show at least the top 3 if they exist, regardless of the 10% rule
            if len(filtered_cities) < 3 and len(cities) > len(filtered_cities):
                filtered_cities = cities[:min(3, len(cities))]
                
            c.largest_cities = ", ".join([f"{name} ({format_pop(pop)})" for name, pop in filtered_cities])

        # Souvenirs, Products, Handicrafts
        q_souv = f"""
        SELECT DISTINCT ?itemLabel WHERE {{
          ?country wdt:P297 "{iso}".
          {{ ?item wdt:P495 ?country. ?item wdt:P31/wdt:P279* ?type. VALUES ?type {{ wd:Q170658 wd:Q11690 wd:Q2095 wd:Q13182 wd:Q202816 }} }}
          UNION {{ ?item wdt:P17 ?country. ?item wdt:P31/wdt:P279* wd:Q202816. }}
          SERVICE wikibase:label {{ bd:serviceParam wikibase:language "pl,en". }}
        }}
        LIMIT 20
        """
        souv_data = await async_sparql_get(q_souv, f"Souvenirs for {iso}")
        s_set = set()
        for r in souv_data:
            val = r.get("itemLabel", {}).get("value")
            if val and not val.startswith("Q") and len(val) > 2:
                s_set.add(val)
        
        if s_set:
            final_souv = ", ".join(sorted(list(s_set))[:8])
            c.practical.souvenirs = final_souv
            c.regional_products = final_souv

        # Religions & Ethnics
        q_cult = f"""
        SELECT ?religionLabel ?religionPercent ?ethnicLabel WHERE {{
          ?country wdt:P297 "{iso}".
          OPTIONAL {{ ?country p:P140 [ ps:P140 ?religion; pq:P2107 ?religionPercent ]. }}
          OPTIONAL {{ ?country wdt:P172 ?ethnic. }}
          SERVICE wikibase:label {{ bd:serviceParam wikibase:language "pl,en". }}
        }}
        LIMIT 50
        """
        cult_data = await async_sparql_get(q_cult, f"Cultural for {iso}")
        rels = {}
        ethnics = set()
        for r in cult_data:
            r_name = r.get("religionLabel", {}).get("value")
            r_perc = r.get("religionPercent", {}).get("value")
            e_name = r.get("ethnicLabel", {}).get("value")
            if r_name and not r_name.startswith("Q"):
                try: p_val = float(r_perc) if r_perc else 0.0
                except: p_val = 0.0
                rels[r_name] = max(rels.get(r_name, 0.0), p_val)
            if e_name and not e_name.startswith("Q"): ethnics.add(e_name)
        
        if ethnics: c.ethnic_groups = ", ".join(sorted(list(ethnics))[:5])
        if rels:
            db.query(models.Religion).filter(models.Religion.country_id == c.id).delete()
            total_perc = sum(rels.values())
            sorted_rels = sorted(rels.items(), key=lambda x: x[1], reverse=True)
            for name, p in sorted_rels[:5]:
                db.add(models.Religion(country_id=c.id, name=name, percentage=p if total_perc > 0 else 0.0))

    # 3. Comprehensive Fallbacks
    REGIONAL_FALLBACKS = {
        'Europe': {'climate': 'Klimat umiarkowany', 'souvenirs': 'Lokalne rękodzieło, Produkty regionalne'},
        'Asia': {'climate': 'Klimat zwrotnikowy / kontynentalny', 'souvenirs': 'Przyprawy, Tekstylia, Herbata'},
        'Africa': {'climate': 'Klimat gorący (pustynny / tropikalny)', 'souvenirs': 'Rzeźby w drewnie, Biżuteria, Tkaniny'},
        'Americas': {'climate': 'Zróżnicowany klimat', 'souvenirs': 'Wyroby rzemieślnicze, Kawa, Lokalne pamiątki'},
        'Oceania': {'climate': 'Klimat oceaniczny / tropikalny', 'souvenirs': 'Muszle, Wyroby z drewna'}
    }

    EXTRA_FALLBACKS = {
        'PL': {'dish': 'Bigos, Pierogi', 'climate': 'Klimat umiarkowany przejściowy', 'souvenirs': 'Bursztyn, Ceramika bolesławiecka, Oscypek', 'website': 'https://www.polska.travel/pl'},
        'AT': {'climate': 'Klimat umiarkowany, alpejski', 'souvenirs': 'Słodycze Manner, Kryształy Swarovski, Olej z pestek dyni', 'website': 'https://www.austria.info/pl'},
        'DE': {'climate': 'Klimat umiarkowany morski i kontynentalny', 'souvenirs': 'Kufle do piwa, Ceramika z Miśni, Marcepan', 'website': 'https://www.germany.travel/en/home.html'},
        'EG': {'climate': 'Klimat zwrotnikowy suchy (pustynny)', 'souvenirs': 'Papirusy, Przyprawy, Bawełna egipska'},
        'TH': {'climate': 'Klimat zwrotnikowy monsunowy', 'souvenirs': 'Jedwab tajski, Produkty kokosowe, Figurki słoni'},
        'FR': {'climate': 'Klimat umiarkowany morski i śródziemnomorski', 'souvenirs': 'Wina, Sery, Perfumy, Berety', 'website': 'https://www.france.fr/pl'},
        'IT': {'climate': 'Klimat śródziemnomorski', 'souvenirs': 'Wyroby skórzane, Oliwa, Szkło weneckie', 'website': 'https://www.italia.it/en'},
        'ES': {'climate': 'Klimat śródziemnomorski i kontynentalny', 'souvenirs': 'Wachlarze, Szafran, Ceramika', 'website': 'https://www.spain.info/en/'},
        'JP': {'climate': 'Zróżnicowany (od podzwrotnikowego po umiarkowany)', 'souvenirs': 'Matcha, Ceramika, Noże kuchenne, Kimono', 'website': 'https://www.japan.travel/en/'},
        'CU': {'climate': 'Klimat podzwrotnikowy (tropikalny)', 'souvenirs': 'Cygara, Rum, Kawa kubańska, Instrumenty perkusyjne, Kapelusze panama'},
    }

    for iso, c in country_map.items():
        fb = EXTRA_FALLBACKS.get(iso)
        if fb:
            if 'dish' in fb: c.national_dish = fb['dish']
            if 'climate' in fb: c.climate_description = fb['climate']
            if 'website' in fb: c.official_tourist_website = fb['website']
            if 'souvenirs' in fb:
                c.regional_products = fb['souvenirs']
                c.practical.souvenirs = fb['souvenirs']

        if iso in country_climates and (not c.climate_description or c.climate_description in [v['climate'] for v in REGIONAL_FALLBACKS.values()]):
            desc = ", ".join(sorted(list(country_climates[iso])))[:250]
            if desc: c.climate_description = desc

        reg_fb = REGIONAL_FALLBACKS.get(c.continent)
        if reg_fb:
            if not c.climate_description: c.climate_description = reg_fb['climate']
            if not c.regional_products:
                c.regional_products = reg_fb['souvenirs']
                if not c.practical.souvenirs: c.practical.souvenirs = reg_fb['souvenirs']
    
    db.commit()

async def sync_things_batch(db: Session, countries: list[models.Country]):
    if not countries: return
    country_map = {c.iso_alpha2.upper(): c for c in countries}
    isos = ' '.join([f'"{iso}"' for iso in country_map.keys()])
    query = f"""
    SELECT DISTINCT ?countryISO ?thingLabel WHERE {{ 
      VALUES ?countryISO {{ {isos} }} 
      ?country wdt:P297 ?countryISO. 
      ?thing wdt:P31/wdt:P279* wd:Q570116; wdt:P17 ?country; wikibase:sitelinks ?sitelinks.
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
    # Batch size 5 is safe for the "detailed" queries we now run per-country inside the batch
    batch_size = 5
    results = {"success": 0, "errors": 0}
    print(f"Syncing extended info for {len(countries)} countries in batches of {batch_size}...")
    for i in range(0, len(countries), batch_size):
        batch = countries[i : i + batch_size]
        print(f"Progress: {i}/{len(countries)} countries...")
        try:
            await sync_wikidata_batch(db, batch)
            await asyncio.sleep(0.2)
            await sync_things_batch(db, batch)
            results["success"] += len(batch)
            db.commit()
        except Exception as e:
            logger.error(f"Error in wikidata batch starting at {i}: {e}")
            results["errors"] += len(batch)
        await asyncio.sleep(0.5)
    return results

async def sync_wikidata_country_info(db: Session, country_iso2: str):
    country = db.query(models.Country).filter(models.Country.iso_alpha2 == country_iso2.upper()).first()
    if country:
        await sync_wikidata_batch(db, [country])
        await sync_things_batch(db, [country])
    return {"status": "done"}
