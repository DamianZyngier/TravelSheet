# Admin Documentation - Data Sources & Features

This document provides technical details about the data sources used in TravelSheet. It is intended for administrators and developers to understand where data comes from, costs, limits, and specific data points.

## Data Sources Summary

| Source | Type | URL | Cost | Limits | UI Category | Sync | Official | Primary Data |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **REST Countries** | API | [restcountries.com](https://restcountries.com) | Free | No strict limits | **Informacje** | Weekly | No | Basic info, ISO codes, coordinates |
| **MSZ gov.pl** | Scraper | [gov.pl](https://www.gov.pl/...) | Free | 1s delay per country | **Bezpieczeństwo** | Daily | Yes | Safety, Visas, Health, Polish Embassies |
| **Wikipedia** | API | [pl.wikipedia.org](https://pl.wikipedia.org) | Free | Generous | **Poznaj kraj** | Weekly | No | Country summaries (descriptions) |
| **Wikidata** | SPARQL | [query.wikidata.org](https://query.wikidata.org) | Free | Strict (batching used) | **Poznaj kraj** | Weekly | No | Attractions, Symbols, Largest cities |
| **NBP** | API | [api.nbp.pl](https://api.nbp.pl) | Free | Very generous | **Waluta** | Daily | Yes | Exchange rates (PLN) |
| **Nager.Date** | API | [date.nager.at](https://date.nager.at) | Free | No strict limits | **Święta** | Weekly | No | Public holidays |
| **OpenWeather** | API | [openweathermap.org](https://openweathermap.org) | Paid/Free | 60 calls / min | **Pogoda** | Monthly | No | Current weather & conditions |
| **UNESCO** | API | [data.unesco.org](https://data.unesco.org) | Free | No strict limits | **Atrakcje** | Weekly | Yes | World Heritage sites info |
| **CDC** | Scraper | [cdc.gov](https://cdc.gov) | Free | Rate-limited | **Zdrowie** | Weekly | Yes | Secondary vaccination info |

## Management Scripts

Use these scripts to keep data fresh:

- **`python scripts/sync_all.py`**: The main entry point. Performs a full synchronization of all sources (UNESCO, Safety, Wikipedia, Holidays, Weather) and exports to JSON.
- **`python scripts/export_to_json.py`**: Only performs the export from the SQLite database to `docs/data.json`.
- **`python scripts/run_unesco_sync.py`**: Syncs only UNESCO data.
- **`python scripts/sync_msz.py`**: Syncs only safety/entry information from gov.pl.

## Testing & Quality Assurance

To ensure data integrity and UI stability, run these tests before committing:

### 1. Data Integrity Test
Validates that `docs/data.json` contains all required fields (safety levels, UNESCO flags, plug types, etc.).
```bash
python scripts/test_data_integrity.py
```

### 2. Frontend Unit Tests
Ensures the UI renders correctly and handles data as expected using Vitest.
```bash
npm test --prefix frontend
```

## Technical Notes
*   **Frontend:** Reads exclusively from `docs/data.json` (static export). No direct database access to ensure high performance and zero server costs (GitHub Pages).
*   **Backend:** FastAPI app used primarily as an orchestrator for scrapers and admin tasks.
*   **UNESCO In-Danger:** The `is_danger` flag is now separate from `category`. A site can be both "Cultural" and "ZAGROŻONE" (in danger).
