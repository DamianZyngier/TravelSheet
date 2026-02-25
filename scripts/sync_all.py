import asyncio
import os
import sys
import logging
import time

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.scrapers import unesco, msz_gov_pl, wiki_summaries, weather, holidays
from scripts.export_to_json import export_all

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)

logger = logging.getLogger("sync_all")

async def run_full_sync():
    start_time = time.time()
    
    print("\n" + "="*50)
    print("🌍 STARTING FULL DATA SYNCHRONIZATION 🌍")
    print("="*50 + "\n")

    db = SessionLocal()
    try:
        # 1. UNESCO Sites
        print("--- [1/6] UNESCO World Heritage Sites ---")
        try:
            u_res = await unesco.sync_unesco_sites(db)
            print(f"✅ {u_res.get('sites_synced', 0)} sites synced across {u_res.get('countries_synced', 0)} countries.\n")
        except Exception as e:
            print(f"❌ UNESCO Sync Error: {e}\n")

        # 2. MSZ Safety Advisories (gov.pl)
        print("--- [2/6] MSZ (gov.pl) Safety & Entry Info ---")
        try:
            s_res = await msz_gov_pl.scrape_all_with_cache(db)
            print(f"✅ Successes: {s_res['success']}, Errors: {s_res['errors']}\n")
        except Exception as e:
            print(f"❌ MSZ Sync Error: {e}\n")

        # 3. Wikipedia Summaries & Wikidata Symbols
        print("--- [3/6] Wikipedia Descriptions & Symbols ---")
        try:
            w_res = await wiki_summaries.sync_all_summaries(db)
            print(f"✅ Successes: {w_res['success']}, Errors: {w_res['errors']}\n")
        except Exception as e:
            print(f"❌ Wikipedia Sync Error: {e}\n")

        # 4. Public Holidays (Nager.Date)
        print("--- [4/6] Public Holidays ---")
        try:
            h_res = await holidays.sync_all_holidays(db)
            print(f"✅ {h_res.get('synced', 0)} countries updated.\n")
        except Exception as e:
            print(f"❌ Holidays Sync Error: {e}\n")

        # 5. Current Weather (OpenWeatherMap)
        print("--- [5/6] Current Weather ---")
        try:
            wt_res = await weather.update_all_weather(db)
            print(f"✅ {wt_res.get('count', 0)} countries updated.\n")
        except Exception as e:
            print(f"❌ Weather Sync Error: {e}\n")

        # 6. Final Export to JSON
        print("--- [6/6] Exporting to docs/data.json ---")
        try:
            export_all()
        except Exception as e:
            print(f"❌ Export Error: {e}\n")

        duration = time.time() - start_time
        print("\n" + "="*50)
        print(f"🎉 FULL SYNC COMPLETED in {duration/60:.1f} minutes!")
        print("="*50 + "\n")

    except Exception as e:
        print(f"\n💥 CRITICAL SYNC ERROR: {e}")
        logger.exception(e)
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(run_full_sync())
