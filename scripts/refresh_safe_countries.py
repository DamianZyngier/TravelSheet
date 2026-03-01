import asyncio
import httpx
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.scrapers import msz_gov_pl
from scripts.export_to_json import export_all

async def refresh():
    db = SessionLocal()
    try:
        await msz_gov_pl.fetch_country_urls()
        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            for iso in ['FR', 'DE']:
                print(f"Refreshing {iso}...")
                await msz_gov_pl.scrape_country(db, iso, client)
        print("Exporting...")
        export_all()
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(refresh())
