# Admin Documentation - Data Sources & Management

Technical details about the data architecture of TripSheet.

## Data Sources Summary

| Source | Type | Cost | Sync | UI Category | Key Data Points |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **REST Countries** | API | Free | Weekly | **Informacje** | ISO codes, Population, Area, Coordinates, Flag URL, Continent, Region |
| **MSZ gov.pl** | Scraper | Free | Daily | **Bezpieczeństwo** | Risk levels (low/medium/high/critical), Safety advisories, Local laws & customs, Embassies, Passport/ID requirements, Visa requirement (PL) |
| **Open-Meteo** | API | Free | Daily | **Pogoda** | **Current weather**, 7-day forecast, Humidity, Wind speed |
| **NBP** | API | Free | Daily | **Waluta** | Live PLN exchange rates (official NBP mid rates) |
| **Wikipedia** | API | Free | Weekly | **Poznaj kraj** | Country summaries (intro), Visa requirements for PL citizens |
| **Wikidata** | SPARQL | API | Weekly | **Wiele sekcji** | Religions (%), Attractions, Symbols, Airports, Railways, Hazards, HDI, Life Expectancy, GDP (Nominal/PPP), Gini, Coat of Arms, Inception date, Official website, Regional products (GI) |
| **UNESCO** | API | Free | Weekly | **Atrakcje** | World Heritage sites, Category, In-danger status, Transnational status, Image, Description |
| **Numbeo** | Scraper | Free | Weekly | **Ceny** | Cost of living indices (Groceries, Restaurants, Transport, Accommodation), **Daily budget estimations** |
| **CDC** | Scraper | Free | Weekly | **Zdrowie** | Required/suggested vaccinations, Health info/warnings |
| **Static Data** | Local | Free | N/A | **Praktiko** | Plug types, Voltage, Frequency, Water safety, Driving side, Timezone, Phone code, Currency code/name, Popular apps, National dish |

## Data Points Catalog (Detailed)

| Category | Field Name | Source Type | Source Name |
| :--- | :--- | :--- | :--- |
| **Basic Info** | ISO Alpha 2/3 | API | REST Countries |
| | Name (PL/EN) | API | REST Countries |
| | Capital | API | REST Countries |
| | Population / Area | API | REST Countries |
| | Continent / Region | API | REST Countries |
| | Coordinates (Lat/Lng) | API | REST Countries |
| | Flag Emoji / URL | API | REST Countries |
| **Safety** | Risk Level / Summary | Scraper | MSZ (gov.pl) |
| | Risk Details | Scraper | MSZ (gov.pl) |
| | MSZ Advisory URL | Scraper | MSZ (gov.pl) |
| **Health** | Vaccinations (Req/Sug) | Scraper | CDC |
| | Health Advice | Scraper | CDC |
| | Tap Water Safety | Local | Static Info |
| | EKUZ Availability | Local | Static Logic |
| **Logistics** | Plug Types / Voltage | Local | Static Info |
| | Driving Side | Local | Static Info |
| | Timezone | API | Wikidata |
| | Phone Code | API | REST Countries |
| | Main Airport | API | Wikidata |
| | Railway Info | API | Wikidata |
| **Entry** | Visa Required (PL) | API/Scraper | Wikipedia / MSZ |
| | Passport / ID Rules | Scraper | MSZ (gov.pl) |
| | Card Acceptance | Scraper | MSZ (gov.pl) |
| | Bargaining Info | Scraper | MSZ (gov.pl) |
| **Finances** | Currency Code / Name | API | REST Countries |
| | Exchange Rate (PLN) | API | NBP |
| | Denominations (Images)| API | MSZ/Local |
| | Cost Indices | Scraper | Numbeo |
| | Daily Budgets | Scraper | Numbeo |
| | Card Acceptance | Scraper | MSZ (gov.pl) |
| **Environment** | Current Weather | API | Open-Meteo |
| | 7-day Forecast | API | Open-Meteo |
| | Climate Averages | API | Open-Meteo |
| | Natural Hazards | API | Wikidata |
| **Culture** | Wiki Summary | API | Wikipedia |
| | Religions (%) | API | Wikidata |
| | UNESCO Sites | API | UNESCO |
| | Top Attractions | API | Wikidata |
| | Laws & Customs | Scraper | MSZ (gov.pl) |
| | Holidays | Scraper | Wikipedia |
| | National Dish/Symbols | API | Wikidata |
| | Popular Apps | Scraper | Wikidata/Local |
| **Socio-Econ** | HDI / Life Expectancy | API | Wikidata |
| | GDP (Nom. / PPP) | API | Wikidata |
| | Gini Coefficient | API | Wikidata |
| | Inception Date | API | Wikidata |
| | Official Website | API | Wikidata |

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
