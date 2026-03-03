# TripSheet - Project Documentation

## Project Overview
TripSheet is a comprehensive travel safety and information portal. It aggregates data from multiple official and public sources to provide travelers with up-to-date information on safety, visas, health, costs, climate, and local laws for every country in the world.

Data is grouped into 5 logical categories for better UX (collapsible accordion style):
1. **Przygotowanie i Formalności** (Docs, Currency, Embassies)
2. **Zdrowie i Bezpieczeństwo** (Health, Safety, Water)
3. **Informacje Praktyczne** (Weather, Plugs, Phones, Costs)
4. **Warunki Środowiskowe** (Climate, Holidays)
5. **Kultura i Atrakcje** (Law, UNESCO, Souvenirs)

The sidebar also supports accordion-style navigation for subcategories.

## Data Validation & Integrity
To ensure high-quality data, the project implements several layers of validation:
- **Database Constraints**: SQLite indices and foreign keys ensure referential integrity.
- **Schema Validation**: Pydantic models in `app/schemas.py` enforce strict rules for ISO codes (2 and 3 characters), geographical coordinates (lat/lng ranges), and percentage values (0-100%).
- **Data Cleaning**: Automated scripts handle edge cases like uninhabited territories (population set to NULL instead of 0) and religious percentage normalization (capping at 100%).
- **Religious Data**: Improved scraping logic to include dominant religions from Wikidata even when exact percentages are unavailable (displayed as "Główne wyznanie" in the UI).
- **Automated Testing**: `scripts/test_data_integrity.py` validates the exported `data.json` structure before deployment.

## Tech Stack
- **Frontend**: React (TypeScript), Vite, Vanilla CSS.
- **Backend/Scrapers**: Python 3.10+, FastAPI, SQLAlchemy, Pydantic, SQLite.
- **Performance**: High-concurrency scraping using `asyncio` and `httpx`.
- **Data Visualization**: react-simple-maps (SVG maps) with custom microstate highlighting.
- **Automation**: GitHub Actions for optimized daily/weekly data synchronization.

## Repository Structure
- `app/`: FastAPI backend and database models.
  - `api/`: API endpoints for data access and administration.
  - `scrapers/`: Parallelized modules for fetching data (MSZ, Wiki, CDC, etc.).
- `frontend/`: React source code and Vitest suite.
- `scripts/`: Production-ready utility scripts for database management, seeding, and export.
- `docs/`: Production build and the main `data.json` file.
- `travel_cheatsheet.db`: Versioned SQLite database (persisted for incremental updates).

## Data Flow
1. **Sync**: GitHub Actions trigger `sync_all.py`.
   - **Daily Mode**: Updates volatile data (FX, Weather, MSZ Safety).
   - **Weekly Mode**: Full refresh of slow-changing data (UNESCO, Wikidata, CDC).
2. **Database**: Scrapers update the versioned SQLite database.
3. **Export**: `export_to_json.py` uses eager loading to convert the DB into `docs/data.json`.
4. **Frontend**: The React app fetches `data.json` at runtime.

## Local Development
### Backend
1. Install dependencies: `pip install -r requirements.txt`
2. Configure environment: Create `.env` from `.env.example` and add `WIKIMEDIA_ACCESS_TOKEN`.
3. Initialize/Update database: `python scripts/sync_all.py --mode daily`
4. Run API: `uvicorn app.main:app --reload`

### Frontend
1. Navigate to directory: `cd frontend`
2. Install dependencies: `npm install`
3. Run dev server: `npm run dev`
4. Run tests: `npm test`

## Data Sources
- **MSZ (gov.pl)**: Safety, Polish-specific advice, and detailed Local Laws/Customs.
- **Wikipedia/Wikidata**: General summaries, visas, attractions, religions, and transport.
- **REST Countries**: Basic geographical data and coordinates.
- **CDC**: Health and vaccinations.
- **UNESCO**: World Heritage sites.
- **Numbeo**: Cost of living and daily budget estimations.
- **Open-Meteo**: 7-day weather forecast and historical climate data.
- **NBP**: Official currency exchange rates to PLN.
