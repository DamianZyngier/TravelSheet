# Admin Documentation - Data Sources & Management

Technical details about the data architecture of TripSheet.

## Data Sources Summary

| Source | Type | Cost | Sync | UI Category | Key Data Points |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **REST Countries** | API | Free | Weekly | **Informacje** | ISO codes, Population, Area, Coordinates |
| **MSZ gov.pl** | Scraper | Free | Daily | **Bezpieczeństwo** | Risk levels, Detailed advisories, Local laws & customs, Embassies |
| **Open-Meteo** | API | Free | Daily | **Pogoda** | **7-day weather forecast**, Historical climate averages |
| **NBP** | API | Free | Daily | **Waluta** | Live PLN exchange rates |
| **Wikipedia** | API | Free | Weekly | **Poznaj kraj** | Country summaries, Visa requirements table |
| **Wikidata** | SPARQL | Free | Weekly | **Wiele sekcji** | Religions (%), Attractions, Symbols, Airports, Railways, Hazards |
| **UNESCO** | API | Free | Weekly | **Atrakcje** | World Heritage sites, In-danger status |
| **Numbeo** | Fallback | Free | Weekly | **Ceny** | Cost of living indices, **Daily budget estimations** |
| **CDC** | Scraper | Free | Weekly | **Zdrowie** | Medical and vaccination requirements |

## Management Scripts

- **`python scripts/sync_all.py --mode [daily|weekly|full]`**: Main orchestrator. 
  - `daily`: Parallel sync of volatile data (~2-5 min).
  - `weekly`/`full`: Full parallel sync of all sources (~15-30 min).
- **`python scripts/export_to_json.py`**: Fast export using SQLAlchemy eager loading.
- **`python scripts/test_sync_tasks.py`**: Integration test that runs a full cycle using a temporary database to verify the pipeline.

## Offline Fallbacks & Resilience

The system is designed to be resilient to API downtime or network issues through various local fallbacks:

| Feature | Fallback Mechanism | File/Source |
| :--- | :--- | :--- |
| **UNESCO** | Uses a local JSON dump if the official API is unreachable. | `data/unesco_fallback.json` |
| **Religions** | Hardcoded statistical data for top ~15 most visited countries. | `app/scrapers/wikidata_info.py` |
| **Cities** | Hardcoded population data for major world capitals and metropolises. | `app/scrapers/wikidata_info.py` |
| **Static Info** | Technical data (plugs, voltage, frequency) is entirely local. | `app/scrapers/static_info.py` |
| **Costs** | Pre-calculated cost-of-living indices for 191 countries. | `app/scrapers/costs.py` |
| **MSZ Safety** | Generic safety advisory text if the specific country page fails to scrape. | `app/scrapers/msz_gov_pl.py` |

## Authentication & APIs

To ensure stability during high-volume Wikidata syncs, the system uses a **Wikimedia Access Token**:
*   Stored in `.env` as `WIKIMEDIA_ACCESS_TOKEN`.
*   Included in `Authorization: Bearer` headers for SPARQL queries.
*   Significantly reduces 429 (Rate Limit) and 504 (Timeout) errors.

## Quality Assurance

### 1. Data Integrity
Validates `data.json` structure and content. Use `--full` for weekly checks.
```bash
python scripts/test_data_integrity.py docs/data.json --full
```

### 2. Frontend & Build
- `npm test`: Runs Vitest suite (16+ tests).
- `BuildIntegrity.test.ts`: Verifies that `docs/index.html` exists and uses relative paths (prevents 404s).

## Technical Architecture
*   **Database Persistence:** `travel_cheatsheet.db` is versioned in Git. This allows GitHub Actions to perform incremental updates instead of starting from scratch, preserving slow-changing data (like UNESCO) during daily runs.
*   **Performance:** All scrapers use `asyncio` with `httpx` and semaphores to maximize speed while respecting target server rate limits.
*   **Export:** Uses Pydantic schemas for validation and SQLAlchemy `joinedload`/`selectinload` to eliminate the N+1 query problem.
*   **Mapping:** Small countries (<15,000 km²) are highlighted with a custom SVG ring/marker in the Map section for better UX.
