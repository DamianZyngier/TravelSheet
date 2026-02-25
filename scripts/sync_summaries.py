import asyncio
import os
import sys
import logging

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.scrapers import wiki_summaries

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)

async def run_sync():
    print("🚀 Starting Wikipedia Summaries synchronization...")
    db = SessionLocal()
    try:
        results = await wiki_summaries.sync_all_summaries(db)
        print("\n--- SYNC SUMMARY ---")
        print(f"✅ Successes: {results['success']}")
        print(f"❌ Errors: {results['errors']}")
    except Exception as e:
        print(f"💥 Critical error: {e}")
    finally:
        db.close()
    print("\nWikipedia Sync completed.")

if __name__ == "__main__":
    asyncio.run(run_sync())
