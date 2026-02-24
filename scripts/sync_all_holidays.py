import asyncio
import os
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.scrapers import holidays

async def main():
    db = SessionLocal()
    print("Rozpoczynam pełną aktualizację świąt...")
    results = await holidays.sync_all_holidays(db)
    print("Zsynchronizowano: " + str(results['synced']))
    db.close()

if __name__ == "__main__":
    asyncio.run(main())
