from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
import os
import asyncio
import logging
import sys

# Konfiguracja logowania do stdout dla GitHub Actions
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger("uvicorn")

from .database import engine, get_db
from . import models, schemas, crud

# Create tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Travel Cheatsheet API",
    description="Polish travel information aggregator",
    version="1.0.0"
)

# CORS - pozwól frontendowi się łączyć
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Produkcyjnie: tylko Twoja domena
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {
        "message": "Travel Cheatsheet API",
        "version": "1.0.0",
        "endpoints": {
            "countries": "/api/countries",
            "country": "/api/countries/{iso_code}",
            "health": "/health"
        }
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}

# Countries endpoints
@app.get("/api/countries", response_model=List[schemas.CountryBasic])
def get_countries(
        skip: int = 0,
        limit: int = 100,
        region: Optional[str] = None,
        db: Session = Depends(get_db)
):
    """Get list of all countries with basic info"""
    countries = crud.get_countries(db, skip=skip, limit=limit, region=region)
    return countries

@app.get("/api/countries/{iso_code}", response_model=schemas.CountryDetail)
def get_country(iso_code: str, db: Session = Depends(get_db)):
    """Get detailed info for specific country (2 or 3 letter ISO code)"""
    iso_code = iso_code.upper()

    if len(iso_code) == 2:
        country = crud.get_country_by_iso2(db, iso_code)
    elif len(iso_code) == 3:
        country = crud.get_country_by_iso3(db, iso_code)
    else:
        raise HTTPException(status_code=400, detail="Invalid ISO code")

    if not country:
        raise HTTPException(status_code=404, detail="Country not found")

    return country

@app.post("/api/admin/sync-rest-countries")
async def sync_rest_countries(db: Session = Depends(get_db)):
    """Admin endpoint - sync data from REST Countries API"""
    from .scrapers.rest_countries import sync_countries

    result = await sync_countries(db)
    return result

@app.post("/api/admin/sync-exchange-rates")
async def sync_exchange_rates(db: Session = Depends(get_db)):
    """Admin endpoint - sync currency exchange rates"""
    from .scrapers.exchange_rates import sync_rates

    result = await sync_rates(db)
    return result

@app.post("/api/admin/sync-static-info")
async def sync_static_info(db: Session = Depends(get_db)):
    """Admin endpoint - sync static info from JSON"""
    from .scrapers.static_info import sync_static_data

    result = sync_static_data(db)
    return result

@app.post("/api/admin/sync-costs")
async def sync_costs_endpoint(db: Session = Depends(get_db)):
    """Admin endpoint - sync cost of living indices"""
    from .scrapers.costs import sync_costs

    result = sync_costs(db)
    return result

@app.post("/api/admin/sync-cdc")
async def sync_cdc_endpoint(db: Session = Depends(get_db)):
    """Admin endpoint - sync vaccinations from CDC"""
    from .scrapers.cdc_health import sync_all_cdc

    result = await sync_all_cdc(db)
    return result

@app.post("/api/admin/sync-unesco-sites")
async def sync_unesco_sites(db: Session = Depends(get_db)):
    """Admin endpoint - sync UNESCO World Heritage sites"""
    from .scrapers.attractions import sync_unesco_sites

    result = await sync_unesco_sites(db)
    return result

@app.post("/api/admin/sync-attractions-wiki")
async def sync_attractions_wiki(db: Session = Depends(get_db)):
    """Admin endpoint - sync top attractions from Wikidata"""
    from .scrapers.wikidata_attractions import sync_all_wiki_attractions

    result = await sync_all_wiki_attractions(db)
    return result

@app.post("/api/admin/sync-embassies")
async def sync_embassies(db: Session = Depends(get_db)):
    """Admin endpoint - sync Polish embassies and consulates"""
    from .scrapers.embassies import scrape_embassies

    result = await scrape_embassies(db)
    return result

@app.post("/api/admin/sync-emergency")
async def sync_emergency(db: Session = Depends(get_db)):
    """Admin endpoint - sync emergency numbers"""
    from .scrapers.emergency import sync_emergency_numbers

    result = await sync_emergency_numbers(db)
    return result

@app.post("/api/admin/sync-holidays")
async def sync_holidays_endpoint(db: Session = Depends(get_db)):
    """Admin endpoint - sync public holidays"""
    from .scrapers.holidays import sync_all_holidays

    result = await sync_all_holidays(db)
    return result

@app.post("/api/admin/sync-climate")
async def sync_climate_endpoint(force: bool = False, db: Session = Depends(get_db)):
    """Admin endpoint - sync climate data from Open-Meteo"""
    from .scrapers.climate import sync_all_climate

    result = await sync_all_climate(db, force=force)
    return result

@app.post("/api/admin/update-weather/{iso_code}")
async def update_weather_endpoint(iso_code: str, db: Session = Depends(get_db)):
    """Admin endpoint - update weather for specific country"""
    from .scrapers.weather import update_weather

    result = await update_weather(db, iso_code.upper())
    return result

@app.post("/api/admin/scrape-gov-pl/{iso_code}")
async def scrape_gov_pl(iso_code: str, db: Session = Depends(get_db)):
    """Admin endpoint - scrape MSZ data for specific country"""
    from .scrapers.gov_pl import scrape_country

    result = await scrape_country(db, iso_code.upper())
    return result

@app.post("/api/admin/scrape-all-gov-pl")
async def scrape_all_gov_pl(db: Session = Depends(get_db)):
    """Admin endpoint - scrape data for ALL countries (with rate limiting and slug cache)"""
    from .scrapers.gov_pl import scrape_all_with_cache

    results = await scrape_all_with_cache(db)
    return results
