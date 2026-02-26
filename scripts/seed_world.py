import asyncio
import os
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal, engine
from app.scrapers import rest_countries, exchange_rates, static_info, unesco, holidays, weather, msz_gov_pl, emergency, climate, costs, wiki_summaries, wikidata_attractions, embassies
from app import models

async def seed_all():
    # Create tables
    models.Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    print("Starting full database seeding...")

    # 1. Sync all countries from REST Countries
    print("Step 1: Syncing all countries from REST Countries...")
    res = await rest_countries.sync_countries(db)
    
    country_count = db.query(models.Country).count()
    if country_count == 0:
        print("CRITICAL ERROR: No countries in database and API sync failed.")
        print("Aborting seed to prevent data loss in export.")
        db.close()
        sys.exit(1) # Exit with error to stop the workflow
        
    if 'error' in res:
        print(f"Warning in Step 1: {res['error']}. Continuing with existing {country_count} countries.")
    else:
        print(f"Synced/Updated {country_count} countries.")

    # 2. Sync currency exchange rates
    print("Step 2: Syncing currency exchange rates...")
    try:
        res = await exchange_rates.sync_rates(db)
        print(f"Updated {res.get('updated', 0)} rates.")
    except Exception as e:
        print(f"Error in Step 2: {e}")

    # 3. Sync static data (plugs, water, etc.)
    print("Step 3: Syncing static data (plugs, water, driving side)...")
    try:
        res = static_info.sync_static_data(db)
        print(f"Synced {res.get('synced', 0)} static records.")
    except Exception as e:
        print(f"Error in Step 3: {e}")

    # 4. Sync UNESCO sites
    print("Step 4: Syncing UNESCO World Heritage sites...")
    try:
        res = await unesco.sync_unesco_sites(db)
        print(f"Synced {res.get('sites_synced', 0)} UNESCO sites.")
    except Exception as e:
        print(f"Error in Step 4: {e}")

    # 4b. Sync Emergency numbers
    print("Step 4b: Syncing emergency numbers...")
    try:
        res = await emergency.sync_emergency_numbers(db)
        print(f"Synced {res.get('synced', 0)} emergency records.")
    except Exception as e:
        print(f"Error in Step 4b: {e}")

    # 4c. Sync Costs
    print("Step 4c: Syncing cost of living indices...")
    try:
        res = costs.sync_costs(db)
        print(f"Synced {res.get('synced', 0)} cost records.")
    except Exception as e:
        print(f"Error in Step 4c: {e}")
    
    # 5. Sync climate data (Open-Meteo)
    print("Step 5: Syncing climate data (this may take a few minutes)...")
    try:
        res = await climate.sync_all_climate(db)
        print(f"Synced climate for {res.get('synced', 0)} countries.")
    except Exception as e:
        print(f"Error in Step 5: {e}")

    # 6. Sync current weather (OpenWeatherMap)
    print("Step 6: Syncing current weather...")
    try:
        # Note: requires OPENWEATHER_API_KEY env var
        await weather.update_all_weather(db)
    except Exception as e:
        print(f"Error in Step 6: {e}")

    # 7. Sync per-country details (MSZ Gov.pl, Holidays)
    countries = db.query(models.Country).all()
    print(f"Step 7: Syncing details for {len(countries)} countries...")

    for i, country in enumerate(countries):
        iso2 = country.iso_alpha2
        print(f"[{i+1}/{len(countries)}] Syncing details for {country.name_pl or country.name} ({iso2})...")
        try:
            await msz_gov_pl.scrape_country(db, iso2)
            await holidays.sync_holidays(db, iso2)
            await wiki_summaries.sync_wiki_summary(db, iso2)
            await wikidata_attractions.sync_wiki_attractions_batch(db, [country])
        except Exception as e: 
            print(f"  - Error: {e}")

    # 8. Sync Embassies
    print("Step 8: Syncing Polish diplomatic missions...")
    try:
        res = await embassies.scrape_embassies(db)
        print(f"Synced missions for {res.get('synced_countries', 0)} countries.")
    except Exception as e:
        print(f"Error in Step 8: {e}")

    # 9. Summary of database content
    print("\nDatabase Summary:")
    entities = [
        ("Countries", models.Country),
        ("Languages", models.Language),
        ("Currencies", models.Currency),
        ("Attractions", models.Attraction),
        ("Unesco Places", models.UnescoPlace),
        ("Holidays", models.Holiday),
        ("Practical Info", models.PracticalInfo),
        ("Safety Info", models.SafetyInfo),
        ("Embassies", models.Embassy)
    ]

    for label, model in entities:
        count = db.query(model).count()
        print(f"{label:18} {count:4} records.")

    db.close()
    print("\nSeeding completed!")

if __name__ == "__main__":
    asyncio.run(seed_all())
