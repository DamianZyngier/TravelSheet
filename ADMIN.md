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
| **UNESCO** | JSON/API | [whc.unesco.org](https://whc.unesco.org) | Free | No strict limits | **Atrakcje** | Weekly | Yes | World Heritage sites info |
| **CDC** | Scraper | [cdc.gov](https://cdc.gov) | Free | Rate-limited | **Zdrowie** | Weekly | Yes | Secondary vaccination info |

## Core Data Sources

### 1. REST Countries API
*   **Type:** API
*   **Source:** [restcountries.com](https://restcountries.com) (Unofficial but widely used open-source aggregator)
*   **Cost:** Free
*   **Limits:** No strict documented limits, but behaves best with filtered fields.
*   **Data Points:**
    *   Basic country info (Name, ISO codes, Capital, Region, Continent).
    *   Languages (Syncs and translates to Polish).
    *   Currencies (Code, Name, Symbol).
    *   Geographic coordinates (Latitude, Longitude).

### 2. MSZ gov.pl (Ministry of Foreign Affairs, Poland)
*   **Type:** Scraper
*   **Source:** [gov.pl](https://www.gov.pl/web/dyplomacja/informacje-dla-podrozujacych) (Official)
*   **Cost:** Free
*   **Limits:** Rate-limited manually in scripts (1s delay between countries).
*   **Data Points:**
    *   **Safety Info:** Risk level (4 levels), safety summaries, detailed warnings.
    *   **Entry Requirements:** Passport/ID requirements, visa necessity.
    *   **Health Info:** Polish-specific health advice.
    *   **Embassies:** Locations, contact details, and websites of Polish diplomatic missions.

### 3. UNESCO World Heritage
*   **Type:** Static Fallback + Official Links
*   **Source:** [UNESCO World Heritage Centre](https://whc.unesco.org) (Official)
*   **Cost:** Free
*   **Data Points:**
    *   List of UNESCO sites per country (up to all known sites).
    *   UNESCO ID (for official linking).
    *   Images (direct links to UNESCO gallery).
    *   Descriptions (Official UNESCO summaries).
    *   Category (Cultural, Natural, Mixed).

### 4. Wikidata (SPARQL)
*   **Type:** API / SPARQL Query
*   **Source:** [Wikidata](https://query.wikidata.org) (Official/Community)
*   **Cost:** Free
*   **Limits:** Strict rate limits on SPARQL endpoint. Optimized in batches of 10 countries with 2s delay.
*   **Data Points:**
    *   **Attractions:** Top 10-15 sights per country based on sitelinks/popularity.
    *   **Wiki Summaries:** Short descriptions of countries.
    *   **National Symbols:** National animal, flower, etc.
    *   **Cities:** Top 5 largest cities by population.
    *   **UNESCO Metadata:** Fetching missing IDs or images via SPARQL.

### 5. NBP API (National Bank of Poland)
*   **Type:** API
*   **Source:** [api.nbp.pl](https://api.nbp.pl) (Official)
*   **Cost:** Free
*   **Limits:** Very generous.
*   **Data Points:**
    *   Exchange rates (Currency code to PLN). Covers major (Table A) and exotic (Table B) currencies.

### 6. OpenWeatherMap
*   **Type:** API
*   **Source:** [openweathermap.org](https://openweathermap.org)
*   **Cost:** Paid (Free tier available)
*   **Limits:** 60 calls/minute. Script uses 1.5s delay (approx 40 calls/min) to stay safe.
*   **Data Points:**
    *   Current temperature, weather condition (text + icon), humidity, wind speed.

### 7. Nager.Date API
*   **Type:** API
*   **Source:** [date.nager.at](https://date.nager.at) (Unofficial/Open Source)
*   **Cost:** Free
*   **Limits:** No strict limits.
*   **Data Points:**
    *   Public holidays for the current year (Local name + Polish translation).

### 8. CDC (Centers for Disease Control and Prevention)
*   **Type:** Scraper
*   **Source:** [cdc.gov](https://wwwnc.cdc.gov/travel) (Official US Govt)
*   **Cost:** Free
*   **Data Points:**
    *   Vaccinations (Required vs. Suggested). Used as a secondary source or fallback to MSZ.

### 9. Static Data (`data/static_data.json`)
*   **Type:** Local JSON
*   **Data Points:**
    *   Power plugs (Types A-N).
    *   Voltage/Frequency.
    *   Tap water safety.
    *   Driving side.

## Synchronization Workflows

*   **Weekly Full Sync (`weekly-sync.yml`):**
    *   Runs on Sundays at 02:00 UTC.
    *   Performs a clean-room sync: Rebuilds SQLite DB, hits all APIs/Scrapers, generates a fresh `docs/data.json`.
*   **Daily Sync (`daily-sync.yml`):**
    *   Updates transient data: Weather, Exchange rates.
    *   Commit changes to `docs/data.json` to keep the frontend "alive".

## Technical Notes
*   **Frontend:** Reads exclusively from `docs/data.json` (static export). No direct database access to ensure high performance and zero server costs (GitHub Pages).
*   **Backend:** FastAPI app used primarily as an orchestrator for scrapers and admin tasks.
