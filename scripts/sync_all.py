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
        # --- PHASE 1: MANDATORY / DAILY (Parallelized where possible) ---
        print("--- PHASE 1: Daily / Mandatory Data ---")
        
        # 1. Basic Country Info (MANDATORY for others)
        print("[1/4] Syncing Basic Country Information...")
        await rest_countries.sync_countries(db)
        
        # 2-4. Exchange Rates, MSZ, Weather (These are independent)
        print("[2-4/4] Syncing Rates, MSZ Safety, and Weather in parallel...")
        await asyncio.gather(
            exchange_rates.sync_rates(db),
            msz_gov_pl.scrape_all_with_cache(db),
            weather.update_all_weather(db)
        )
        print("✅ Phase 1 completed.\n")

        # --- PHASE 2: WEEKLY / SLOW CHANGING (Parallelized) ---
        if mode == "full" or mode == "weekly":
            print("--- PHASE 2: Weekly / slow-changing Data ---")
            
            # Grouping independent scrapers to run in parallel
            # Group A: Fast static/local data
            print("[5-8/15] Syncing Static Info, UNESCO, Emergency, and Costs...")
            # Note: unesco and emergency are async, static_info and costs are sync
            # We run sync ones first or wrap them
            static_info.sync_static_data(db)
            costs.sync_costs(db)
            
            await asyncio.gather(
                unesco.sync_unesco_sites(db),
                emergency.sync_emergency_numbers(db)
            )

            # Group B: External API heavy data
            print("[9-12/15] Syncing Climate, Wiki Summaries, Holidays, and CDC...")
            await asyncio.gather(
                climate.sync_all_climate(db, force=True),
                wiki_summaries.sync_all_summaries(db),
                holidays.sync_all_holidays(db),
                cdc_health.sync_all_cdc(db)
            )

            # Group C: Scrapers & Wikidata (Wikidata is sensitive to parallel load, we run these last)
            print("[13-15/15] Syncing Embassies and Wikidata...")
            await embassies.scrape_embassies(db)
            
            # We run wikidata scrapers sequentially to avoid 429/5xx errors
            await wikidata_attractions.sync_all_wiki_attractions(db)
            await wikidata_info.sync_all_wikidata_info(db)
            
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
