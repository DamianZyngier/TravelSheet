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

def log_result(name, result):
    """Helper to log scraper results in a standard way"""
    if not result or not isinstance(result, dict):
        print(f"✅ {name}: Sync completed (no detailed stats)")
        return
        
    success = result.get("success", result.get("updated", result.get("synced", 0)))
    errors = result.get("errors", 0)
    
    # Handle case where errors might be a list of messages
    error_count = len(errors) if isinstance(errors, list) else int(errors)
    
    if error_count > 0:
        print(f"⚠️ {name}: {success} OK, {error_count} ERRORS")
    else:
        print(f"✅ {name}: {success} OK")

async def run_sync(mode="full"):
    start_time = time.time()
    
    print("\n" + "="*50)
    print(f"🌍 STARTING {mode.upper()} DATA SYNCHRONIZATION 🌍")
    print("="*50 + "\n")

    # Create tables if they don't exist
    models.Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        # --- PHASE 1: MANDATORY / DAILY (Parallelized where possible) ---
        print("--- PHASE 1: Daily / Mandatory Data ---")
        
        # 1. Basic Country Info (MANDATORY for others)
        print("[1/4] Syncing Basic Country Information...")
        res_basic = await rest_countries.sync_countries(db)
        log_result("Basic Info", res_basic)
        
        # 2-4. Exchange Rates, MSZ, Weather (These are independent)
        print("[2-4/4] Syncing Rates, MSZ Safety, and Weather in parallel...")
        results = await asyncio.gather(
            exchange_rates.sync_rates(db),
            msz_gov_pl.scrape_all_with_cache(db),
            weather.update_all_weather(db)
        )
        log_result("Exchange Rates", results[0])
        log_result("MSZ Safety", results[1])
        log_result("Weather", results[2])
        print("✅ Phase 1 completed.\n")

        # --- PHASE 2: WEEKLY / SLOW CHANGING (Parallelized) ---
        if mode == "full" or mode == "weekly":
            print("--- PHASE 2: Weekly / slow-changing Data ---")
            
            # Grouping independent scrapers to run in parallel
            # Group A: Fast static/local data
            print("[5-8/15] Syncing Static Info, UNESCO, Emergency, and Costs...")
            static_info.sync_static_data(db)
            res_costs = costs.sync_costs(db)
            
            res_unesco, res_emergency = await asyncio.gather(
                unesco.sync_unesco_sites(db),
                emergency.sync_emergency_numbers(db)
            )
            log_result("Costs", res_costs)
            log_result("UNESCO", res_unesco)
            log_result("Emergency", res_emergency)

            # Group B: External API heavy data
            print("[9-12/15] Syncing Climate, Wiki Summaries, Holidays, and CDC...")
            res_group_b = await asyncio.gather(
                climate.sync_all_climate(db, force=True),
                wiki_summaries.sync_all_summaries(db),
                holidays.sync_all_holidays(db),
                cdc_health.sync_all_cdc(db)
            )
            log_result("Climate", res_group_b[0])
            log_result("Wiki Summaries", res_group_b[1])
            log_result("Holidays", res_group_b[2])
            log_result("CDC Health", res_group_b[3])

            # Group C: Scrapers & Wikidata (Wikidata is sensitive to parallel load, we run these last)
            print("[13-15/15] Syncing Embassies and Wikidata...")
            res_embassies = await embassies.scrape_embassies(db)
            log_result("Embassies", res_embassies)
            
            # We run wikidata scrapers sequentially to avoid 429/5xx errors
            res_wiki_attr = await wikidata_attractions.sync_all_wiki_attractions(db)
            log_result("Wiki Attractions", res_wiki_attr)
            
            res_wiki_info = await wikidata_info.sync_all_wikidata_info(db)
            log_result("Wiki Info (Religions/Ethnics)", res_wiki_info)
            
            print("✅ Phase 2 completed.\n")

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
