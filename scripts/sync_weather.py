import asyncio
import os
import sys
import logging

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.scrapers import weather

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)

async def run_sync():
    print("🌤️ Starting Weather synchronization (OpenWeatherMap)...")
    db = SessionLocal()
    try:
        # This will send ~250 requests (one per capital)
        # It's rate limited to ~45 calls/min in the scraper
        results = await weather.update_all_weather(db)
        print("\n--- SYNC SUMMARY ---")
        print(f"✅ Completed: {results['count']} countries updated.")
    except Exception as e:
        print(f"💥 Critical error: {e}")
    finally:
        db.close()
    print("\nWeather Sync completed.")

if __name__ == "__main__":
    asyncio.run(run_sync())
