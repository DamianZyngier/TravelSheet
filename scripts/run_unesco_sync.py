import asyncio
import os
import sys

# Dodanie głównego katalogu do ścieżki
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app.scrapers import unesco

async def main():
    print("Inicjuję pobieranie danych UNESCO z data.unesco.org...")
    db = SessionLocal()
    try:
        result = await unesco.sync_unesco_sites(db)
        status = result.get('status')
        countries = result.get('countries_synced')
        sites = result.get('sites_synced')
        source = result.get('source')
        print(f"Status: {status}")
        print(f"Zsynchronizowano krajów: {countries}")
        print(f"Zsynchronizowano obiektów: {sites}")
        print(f"Źródło: {source}")
    except Exception as e:
        print(f"Błąd podczas synchronizacji: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(main())
