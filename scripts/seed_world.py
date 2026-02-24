import asyncio
import os
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal, engine
from app.scrapers import rest_countries, exchange_rates, static_info, attractions, holidays, weather, gov_pl
from app import models

async def seed_all():
    # Create tables
    models.Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    print("Starting full database seeding...")

    # 1. Sync all countries from REST Countries
    print("Step 1: Syncing all countries from REST Countries...")
    res = await rest_countries.sync_countries(db)
    if 'error' in res:
        print(f"Error in Step 1: {res['error']}")
    else:
        print(f"Synced {res['synced']} countries.")

    # 2. Sync currency exchange rates
    print("Step 2: Syncing currency exchange rates...")
    res = await exchange_rates.sync_rates(db)
    if 'error' in res:
        print(f"Error in Step 2: {res['error']}")
    else:
        print(f"Updated {res['updated']} rates.")

    # 3. Sync static data (plugs, water, etc.)
    print("Step 3: Syncing static data (plugs, water, driving side)...")
    res = static_info.sync_static_data(db)
    if 'error' in res:
        print(f"Error in Step 3: {res['error']}")
    else:
        print(f"Synced {res['synced']} static records.")

    # 4. Sync UNESCO sites
    print("Step 4: Syncing UNESCO World Heritage sites...")
    res = await attractions.sync_unesco_sites(db)
    if 'error' in res:
        print(f"Error in Step 4: {res['error']}")
    else:
        print(f"Synced {res['synced']} UNESCO sites.")

    # 5. Sync per-country details (Gov.pl, Holidays, Weather)
    # We'll do this for a subset or all depending on time
    countries = db.query(models.Country).all()
    print(f"Step 5: Syncing details for {len(countries)} countries (with rate limits)...")

    for i, country in enumerate(countries):
        iso2 = country.iso_alpha2
        name = country.name_pl or country.name
        print(f"[{i+1}/{len(countries)}] Processing {name} ({iso2})...")
        
        # Gov.pl (MSZ)
        try:
            await gov_pl.scrape_country(db, iso2)
        except Exception as e: 
            print(f"  - MSZ Error for {iso2}: {e}")
            pass

        # Holidays
        try:
            await holidays.sync_holidays(db, iso2)
        except: pass

        # Weather (Only if API key is present)
        #if os.getenv("OPENWEATHER_API_KEY"):
        #    try:
        #        await weather.update_weather(db, iso2)
        #    except: pass

        # Rate limiting: MSZ & OpenHolidays don't have strict limits, but let's be kind.
        # OpenWeather has 60/min
        #await asyncio.sleep(1)

    # 6. Summary of database content
    print("\nDatabase Summary:")
    
    entities = [
        ("Countries", models.Country),
        ("Languages", models.Language),
        ("Currencies", models.Currency),
        ("Attractions", models.Attraction),
        ("Holidays", models.Holiday),
        ("Practical Info", models.PracticalInfo),
        ("Laws & Customs", models.LawAndCustom),
        ("Safety Info", models.SafetyInfo),
        ("Embassies", models.Embassy),
        ("Weather", models.Weather)
    ]

    for label, model in entities:
        count = db.query(model).count()
        samples = db.query(model).limit(3).all()
        sample_str = ", ".join([str(s) for s in samples])
        if count > 3:
            sample_str += "..."
        print(f"{label:18} {count:4} records. Samples: [{sample_str}]")

    db.close()
    print("\nSeeding completed!")

if __name__ == "__main__":
    asyncio.run(seed_all())
