# TripSheet - Project Documentation

## Project Overview
TripSheet is a comprehensive travel safety and information portal. It aggregates data from multiple official and public sources to provide travelers with up-to-date information on safety, visas, health, costs, climate, and local laws for every country in the world.

## Tech Stack
- **Frontend**: React (TypeScript), Vite, Vanilla CSS.
- **Backend/Scrapers**: Python 3.10+, FastAPI, SQLAlchemy, Pydantic, SQLite.
- **Performance**: High-concurrency scraping using `asyncio` and `httpx`.
- **Data Visualization**: react-simple-maps (SVG maps) with custom microstate highlighting.
- **Automation**: GitHub Actions for optimized daily/weekly data synchronization.

## Repository Structure
- `app/`: FastAPI backend and database models.
  - `api/`: API endpoints for data access and administration.
  - `scrapers/`: Parallelized modules for fetching data (MSZ, Wiki, UNESCO, etc.).
- `frontend/`: React source code and Vitest suite.
- `scripts/`: Utility scripts for database management, migration, and eager-loading export.
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
