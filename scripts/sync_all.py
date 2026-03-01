import asyncio
import os
import sys
import logging
import time
import argparse

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal, engine
from app import models
from app.scrapers import (
    unesco, msz_gov_pl, wiki_summaries, weather, holidays, 
    costs, cdc_health, embassies, emergency, climate, 
    rest_countries, exchange_rates, static_info, 
    wikidata_attractions, wikidata_info
)
from scripts.export_to_json import export_all

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)

logger = logging.getLogger("sync_all")

async def run_sync(mode="full"):
    start_time = time.time()
    
    print("\n" + "="*50)
    print(f"🌍 STARTING {mode.upper()} DATA SYNCHRONIZATION 🌍")
    print("="*50 + "\n")

    # Create tables if they don't exist
    models.Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        # --- PHASE 1: MANDATORY / DAILY ---
        
        # 1. Basic Country Info (REST Countries)
        print("--- [1] Basic Country Information ---")
        await rest_countries.sync_countries(db)
        print(f"✅ Synced/Updated {db.query(models.Country).count()} countries.\n")

        # 2. Exchange Rates
        print("--- [2] Currency Exchange Rates ---")
        await exchange_rates.sync_rates(db)
        print("✅ Rates updated.\n")

        # 3. MSZ Safety Advisories (gov.pl)
        print("--- [3] MSZ (gov.pl) Safety & Entry Info ---")
        await msz_gov_pl.scrape_all_with_cache(db)
        print("✅ MSZ advisories updated.\n")

        # 4. Current Weather
        print("--- [4] Current Weather ---")
        await weather.update_all_weather(db)
        print("✅ Weather updated.\n")

        # --- PHASE 2: WEEKLY / SLOW CHANGING ---
        
        if mode == "full" or mode == "weekly":
            # 5. Static Info (Plugs, Water, Driving)
            print("--- [5] Static Practical Info ---")
            static_info.sync_static_data(db)
            print("✅ Static records synced.\n")

            # 6. UNESCO Sites
            print("--- [6] UNESCO World Heritage Sites ---")
            u_res = await unesco.sync_unesco_sites(db)
            if u_res.get('sites_synced', 0) == 0 and mode == "weekly":
                raise Exception("UNESCO sync returned 0 sites!")
            print(f"✅ UNESCO sites synced.\n")

            # 7. Emergency Numbers
            print("--- [7] Emergency Numbers ---")
            await emergency.sync_emergency_numbers(db)
            print("✅ Emergency numbers synced.\n")

            # 8. Costs (Numbeo)
            print("--- [8] Cost of Living Indices ---")
            costs.sync_costs(db)
            print("✅ Cost records synced.\n")

            # 9. Climate
            print("--- [9] Climate Data ---")
            await climate.sync_all_climate(db, force=True)
            print("✅ Climate data synced.\n")

            # 10. Wikipedia Summaries
            print("--- [10] Wikipedia Descriptions ---")
            await wiki_summaries.sync_all_summaries(db)
            print("✅ Wikipedia summaries updated.\n")

            # 11. Public Holidays
            print("--- [11] Public Holidays ---")
            await holidays.sync_all_holidays(db)
            print("✅ Holidays updated.\n")

            # 12. CDC Health Info
            print("--- [12] CDC Health & Vaccinations ---")
            await cdc_health.sync_all_cdc(db)
            print("✅ CDC info updated.\n")

            # 13. Embassies
            print("--- [13] Polish Embassies ---")
            await embassies.scrape_embassies(db)
            if db.query(models.Embassy).count() == 0 and mode == "weekly":
                raise Exception("Embassy sync returned 0 embassies!")
            print("✅ Embassies updated.\n")

            # 14. Wikidata Attractions
            print("--- [14] Wikidata Attractions ---")
            attr_res = await wikidata_attractions.sync_all_wiki_attractions(db)
            if attr_res.get('total_attractions', 0) == 0 and mode == "weekly":
                print("⚠️ Attractions returned 0, retrying once...")
                await asyncio.sleep(5)
                attr_res = await wikidata_attractions.sync_all_wiki_attractions(db)
                if attr_res.get('total_attractions', 0) == 0:
                    raise Exception("Attractions sync returned 0 records after retry!")
            print("✅ Attractions synced.\n")

            # 15. Wikidata Extended Info
            print("--- [15] Wikidata Extended Info ---")
            await wikidata_info.sync_all_wikidata_info(db)
            print("✅ Wikidata info updated.\n")

        # FINAL Export to JSON
        print("--- Final Exporting to docs/data.json ---")
        export_all()

        duration = time.time() - start_time
        print("\n" + "="*50)
        print(f"🎉 {mode.upper()} SYNC COMPLETED in {duration/60:.1f} minutes!")
        print("="*50 + "\n")

    except Exception as e:
        print(f"\n💥 CRITICAL SYNC ERROR: {e}")
        logger.exception(e)
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Sync travel data')
    parser.add_argument('--mode', choices=['daily', 'weekly', 'full'], default='full',
                        help='Sync mode (daily: fast data, weekly/full: all data)')
    args = parser.parse_args()
    
    asyncio.run(run_sync(args.mode))
