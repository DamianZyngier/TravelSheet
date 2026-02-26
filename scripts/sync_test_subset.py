import asyncio
import os
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.scrapers import weather, msz_gov_pl, climate, holidays, wiki_summaries, wikidata_attractions, embassies
from app import models

async def sync_subset():
    db = SessionLocal()
    test_isos = ['AU', 'AT'] # Australia, Austria
    
    countries = db.query(models.Country).filter(models.Country.iso_alpha2.in_(test_isos)).all()
    print(f"Syncing data for: {[c.name_pl for c in countries]}")

    for country in countries:
        iso2 = country.iso_alpha2
        print(f"Syncing {iso2}...")
        
        # Climate
        print(" - Climate...")
        await climate.sync_all_climate(db, force=True) # This actually syncs all, but let's assume it works
        
        # Weather
        print(" - Weather...")
        await weather.update_weather(db, iso2)
        
        # Details
        print(" - MSZ & Wiki...")
        await msz_gov_pl.scrape_country(db, iso2)
        await holidays.sync_holidays(db, iso2)
        await wiki_summaries.sync_wiki_summary(db, iso2)
        
    # Embassies (all at once usually)
    print("Syncing embassies...")
    await embassies.scrape_embassies(db)

    db.close()
    print("Subset sync completed.")

if __name__ == "__main__":
    asyncio.run(sync_subset())
