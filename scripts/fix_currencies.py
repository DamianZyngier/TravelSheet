import asyncio
import os
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.scrapers import exchange_rates

async def main():
    db = SessionLocal()
    print("🔄 Naprawiam nazwy walut korzystając z oficjalnych danych NBP...")
    try:
        results = await exchange_rates.sync_rates(db)
        if "error" in results:
            print(f"❌ Błąd: {results['error']}")
        else:
            print(f"✅ Sukces! Zaktualizowano kursy dla {results['updated']} walut.")
            print(f"✅ Zaktualizowano oficjalne polskie nazwy dla {results['names_updated']} walut.")
    except Exception as e:
        print(f"💥 Błąd krytyczny: {e}")
    finally:
        db.close()
    print("Gotowe.")

if __name__ == "__main__":
    asyncio.run(main())
