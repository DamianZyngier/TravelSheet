import asyncio
import os
import sys
import logging

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.scrapers import gov_pl

# Configure logging for CI
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)

async def run_sync():
    print("Starting MSZ (gov.pl) synchronization script...")
    db = SessionLocal()
    try:
        results = await gov_pl.scrape_all_with_cache(db)
        print("\n--- SYNC SUMMARY ---")
        print(f"Successes: {results['success']}")
        print(f"Errors: {results['errors']}")
        if results['details']:
            print("\nError details:")
            for detail in results['details'][:20]: # Show first 20 errors
                print(f" - {detail}")
    finally:
        db.close()
    print("MSZ Sync completed.")

if __name__ == "__main__":
    asyncio.run(run_sync())
