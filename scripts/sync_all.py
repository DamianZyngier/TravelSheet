import asyncio
import os
import sys
import logging
import time

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app import models
from app.scrapers import unesco, msz_gov_pl, wiki_summaries, weather, holidays, costs, cdc_health, embassies, emergency, climate, rest_countries, exchange_rates, static_info, wikidata_attractions
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
        # 1. Basic Country Info (REST Countries)
        print("--- [1/14] Basic Country Information ---")
        try:
            r_res = await rest_countries.sync_countries(db)
            print(f"✅ Synced/Updated {db.query(models.Country).count()} countries.\n")
        except Exception as e:
            print(f"❌ REST Countries Sync Error: {e}\n")

        # 2. Exchange Rates
        print("--- [2/14] Currency Exchange Rates ---")
        try:
            ex_res = await exchange_rates.sync_rates(db)
            print(f"✅ Updated {ex_res.get('updated', 0)} rates.\n")
        except Exception as e:
            print(f"❌ Exchange Rates Sync Error: {e}\n")

        # 3. Static Info (Plugs, Water, Driving)
        print("--- [3/14] Static Practical Info ---")
        try:
            st_res = static_info.sync_static_data(db)
            print(f"✅ Synced {st_res.get('synced', 0)} static records.\n")
        except Exception as e:
            print(f"❌ Static Info Sync Error: {e}\n")

        # 4. UNESCO Sites
        print("--- [4/14] UNESCO World Heritage Sites ---")
        try:
            u_res = await unesco.sync_unesco_sites(db)
            print(f"✅ {u_res.get('sites_synced', 0)} sites synced across {u_res.get('countries_synced', 0)} countries.\n")
        except Exception as e:
            print(f"❌ UNESCO Sync Error: {e}\n")

        # 5. Emergency Numbers
        print("--- [5/14] Emergency Numbers ---")
        try:
            em_res = await emergency.sync_emergency_numbers(db)
            print(f"✅ Synced {em_res.get('synced', 0)} records.\n")
        except Exception as e:
            print(f"❌ Emergency Sync Error: {e}\n")

        # 6. Costs (Numbeo)
        print("--- [6/14] Cost of Living Indices ---")
        try:
            c_res = costs.sync_costs(db)
            print(f"✅ Synced {c_res.get('synced', 0)} cost records.\n")
        except Exception as e:
            print(f"❌ Costs Sync Error: {e}\n")

        # 7. Climate
        print("--- [7/14] Climate Data ---")
        try:
            cl_res = await climate.sync_all_climate(db, force=True)
            print(f"✅ Climate data synced.\n")
        except Exception as e:
            print(f"❌ Climate Sync Error: {e}\n")

        # 8. MSZ Safety Advisories (gov.pl)
        print("--- [8/14] MSZ (gov.pl) Safety & Entry Info ---")
        try:
            s_res = await msz_gov_pl.scrape_all_with_cache(db)
            print(f"✅ Successes: {s_res['success']}, Errors: {s_res['errors']}\n")
        except Exception as e:
            print(f"❌ MSZ Sync Error: {e}\n")

        # 9. Wikipedia Summaries & Wikidata Symbols
        print("--- [9/14] Wikipedia Descriptions & Symbols ---")
        try:
            w_res = await wiki_summaries.sync_all_summaries(db)
            print(f"✅ Successes: {w_res['success']}, Errors: {w_res['errors']}\n")
        except Exception as e:
            print(f"❌ Wikipedia Sync Error: {e}\n")

        # 10. Public Holidays (Nager.Date)
        print("--- [10/14] Public Holidays ---")
        try:
            h_res = await holidays.sync_all_holidays(db)
            print(f"✅ {h_res.get('synced', 0)} countries updated.\n")
        except Exception as e:
            print(f"❌ Holidays Sync Error: {e}\n")

        # 11. CDC Health Info
        print("--- [11/14] CDC Health & Vaccinations ---")
        try:
            cdc_res = await cdc_health.sync_all_cdc(db)
            print(f"✅ CDC info updated.\n")
        except Exception as e:
            print(f"❌ CDC Sync Error: {e}\n")

        # 12. Embassies
        print("--- [12/14] Polish Embassies ---")
        try:
            emb_res = await embassies.scrape_embassies(db)
            print(f"✅ Embassies updated.\n")
        except Exception as e:
            print(f"❌ Embassies Sync Error: {e}\n")

        # 13. Current Weather (OpenWeatherMap)
        print("--- [13/14] Current Weather ---")
        try:
            wt_res = await weather.update_all_weather(db)
            print(f"✅ {wt_res.get('count', 0)} countries updated.\n")
        except Exception as e:
            print(f"❌ Weather Sync Error: {e}\n")

        # 14. Wikidata Attractions
        print("--- [14/14] Wikidata Attractions ---")
        try:
            attr_res = await wikidata_attractions.sync_all_wiki_attractions(db)
            print(f"✅ {attr_res.get('total_attractions', 0)} attractions synced across {attr_res.get('synced_countries', 0)} countries.\n")
        except Exception as e:
            print(f"❌ Attractions Sync Error: {e}\n")

        # FINAL Export to JSON
        print("--- Final Exporting to docs/data.json ---")
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
