# TravelSheet - Project Documentation

## Project Overview
TravelSheet is a comprehensive travel safety and information portal. it aggregates data from multiple official and public sources to provide travelers with up-to-date information on safety, visas, health, costs, and climate for every country in the world.

## Tech Stack
- **Frontend**: React (TypeScript), Vite, Vanilla CSS.
- **Backend/Scrapers**: Python 3.10+, FastAPI, SQLAlchemy, SQLite.
- **Data Visualization**: react-simple-maps (SVG maps).
- **Automation**: GitHub Actions for daily/weekly data synchronization.

## Repository Structure
- `app/`: FastAPI backend and database models.
  - `api/`: API endpoints for data access and administration.
  - `scrapers/`: Individual modules for fetching data from various sources (MSZ, Wiki, UNESCO, etc.).
- `frontend/`: React source code.
- `scripts/`: Utility scripts for database seeding, migration, and export.
- `docs/`: Production build and the main `data.json` file served via GitHub Pages.
- `data/`: Fallback and static data files.

## Data Flow
1. **Sync**: GitHub Actions trigger Python scripts that run scrapers.
2. **Database**: Scrapers update the local SQLite database (`travel_cheatsheet.db`).
3. **Export**: The `export_to_json.py` script converts the database into a single `docs/data.json` file.
4. **Frontend**: The React app fetches `data.json` at runtime to display all information.

## Local Development
### Backend
1. Install dependencies: `pip install -r requirements.txt`
2. Initialize database: `python scripts/seed_db.py`
3. Run API: `uvicorn app.main:app --reload`

### Frontend
1. Navigate to directory: `cd frontend`
2. Install dependencies: `npm install`
3. Run dev server: `npm run dev`

## Data Sources
We use multiple sources to ensure data consistency:
- MSZ (gov.pl) for safety and Polish-specific advice.
- Wikipedia/Wikidata for general summaries, visas, and attractions.
- REST Countries for basic geographical data.
- CDC for health and vaccinations.
- UNESCO for World Heritage sites.
- Numbeo for cost of living estimations.
- OpenWeatherMap & Open-Meteo for weather/climate.
