import asyncio
import os
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal, engine
from app.scrapers import rest_countries
from app import models

async def seed_basic():
    # Create tables
    models.Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    print("Starting basic database seeding (Countries only)...")

    # 1. Sync all countries from REST Countries
    print("Step 1: Syncing all countries from REST Countries...")
    res = await rest_countries.sync_countries(db)
    
    country_count = db.query(models.Country).count()
    if country_count == 0:
        print("CRITICAL ERROR: No countries in database and API sync failed.")
        db.close()
        sys.exit(1)
        
    print(f"Synced/Updated {country_count} countries.")
    db.close()
    print("Basic seeding completed!")

if __name__ == "__main__":
    asyncio.run(seed_basic())
