import asyncio
import os
import sys
import logging
import time

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

async def run_full_sync():
    start_time = time.time()
    
    print("\n" + "="*50)
    print("🌍 STARTING FULL DATA SYNCHRONIZATION 🌍")
    print("="*50 + "\n")

    # Create tables if they don't exist
    models.Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        # 1. Basic Country Info (REST Countries) - MANDATORY
        print("--- [1/15] Basic Country Information ---")
        r_res = await rest_countries.sync_countries(db)
        print(f"✅ Synced/Updated {db.query(models.Country).count()} countries.\n")

        # 2. Exchange Rates
        print("--- [2/15] Currency Exchange Rates ---")
        ex_res = await exchange_rates.sync_rates(db)
        print(f"✅ Updated {ex_res.get('updated', 0)} rates.\n")

        # 3. Static Info (Plugs, Water, Driving)
        print("--- [3/15] Static Practical Info ---")
        st_res = static_info.sync_static_data(db)
        print(f"✅ Synced {st_res.get('synced', 0)} static records.\n")

        # 4. UNESCO Sites - MANDATORY for CI
        print("--- [4/15] UNESCO World Heritage Sites ---")
        u_res = await unesco.sync_unesco_sites(db)
        if u_res.get('sites_synced', 0) == 0:
            raise Exception("UNESCO sync returned 0 sites!")
        print(f"✅ {u_res.get('sites_synced', 0)} sites synced across {u_res.get('countries_synced', 0)} countries.\n")

        # 5. Emergency Numbers
        print("--- [5/15] Emergency Numbers ---")
        em_res = await emergency.sync_emergency_numbers(db)
        print(f"✅ Synced {em_res.get('synced', 0)} records.\n")

        # 6. Costs (Numbeo)
        print("--- [6/15] Cost of Living Indices ---")
        c_res = costs.sync_costs(db)
        print(f"✅ Synced {c_res.get('synced', 0)} cost records.\n")

        # 7. Climate
        print("--- [7/15] Climate Data ---")
        await climate.sync_all_climate(db, force=True)
        print(f"✅ Climate data synced.\n")

        # 8. MSZ Safety Advisories (gov.pl)
        print("--- [8/15] MSZ (gov.pl) Safety & Entry Info ---")
        s_res = await msz_gov_pl.scrape_all_with_cache(db)
        print(f"✅ Successes: {s_res['success']}, Errors: {s_res['errors']}\n")

        # 9. Wikipedia Summaries & Wikidata Symbols
        print("--- [9/15] Wikipedia Descriptions & Symbols ---")
        w_res = await wiki_summaries.sync_all_summaries(db)
        print(f"✅ Successes: {w_res['success']}, Errors: {w_res['errors']}\n")

        # 10. Public Holidays (Nager.Date)
        print("--- [10/15] Public Holidays ---")
        h_res = await holidays.sync_all_holidays(db)
        print(f"✅ {h_res.get('synced', 0)} countries updated.\n")

        # 11. CDC Health Info
        print("--- [11/15] CDC Health & Vaccinations ---")
        await cdc_health.sync_all_cdc(db)
        print(f"✅ CDC info updated.\n")

        # 12. Embassies - MANDATORY for CI
        print("--- [12/15] Polish Embassies ---")
        await embassies.scrape_embassies(db)
        emb_count = db.query(models.Embassy).count()
        if emb_count == 0:
            raise Exception("Embassy sync returned 0 embassies!")
        print(f"✅ Embassies updated ({emb_count} total).\n")

        # 13. Current Weather (OpenWeatherMap)
        print("--- [13/15] Current Weather ---")
        wt_res = await weather.update_all_weather(db)
        print(f"✅ {wt_res.get('count', 0)} countries updated.\n")

        # 14. Wikidata Attractions - MANDATORY for CI
        print("--- [14/15] Wikidata Attractions ---")
        attr_res = await wikidata_attractions.sync_all_wiki_attractions(db)
        if attr_res.get('total_attractions', 0) == 0:
            # We retry once if 0, because Wikidata sometimes fails
            print("⚠️ Attractions returned 0, retrying once...")
            await asyncio.sleep(5)
            attr_res = await wikidata_attractions.sync_all_wiki_attractions(db)
            if attr_res.get('total_attractions', 0) == 0:
                raise Exception("Attractions sync returned 0 records after retry!")
        print(f"✅ {attr_res.get('total_attractions', 0)} attractions synced across {attr_res.get('synced_countries', 0)} countries.\n")

        # 15. Wikidata Extended Info (Religions, Transport, Laws)
        print("--- [15/15] Wikidata Extended Info ---")
        await wikidata_info.sync_all_wikidata_info(db)
        print(f"✅ Wikidata info updated.\n")

        # FINAL Export to JSON
        print("--- Final Exporting to docs/data.json ---")
        export_all()

        duration = time.time() - start_time
        print("\n" + "="*50)
        print(f"🎉 FULL SYNC COMPLETED in {duration/60:.1f} minutes!")
        print("="*50 + "\n")

    except Exception as e:
        print(f"\n💥 CRITICAL SYNC ERROR: {e}")
        logger.exception(e)
        sys.exit(1) # Fail the script and the workflow
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(run_full_sync())
