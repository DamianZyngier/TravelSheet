import asyncio
import os
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.scrapers import rest_countries

async def main():
    db = SessionLocal()
    print("Synchronizuję podstawowe dane krajów (ludność, nr kierunkowy)...")
    results = await rest_countries.sync_countries(db)
    print(f"Zsynchronizowano: {results['synced']}, Zaktualizowano: {results['updated']}")
    db.close()

if __name__ == "__main__":
    asyncio.run(main())
