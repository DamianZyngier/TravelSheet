from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ...database import get_db

router = APIRouter()

@router.post("/sync-rest-countries")
async def sync_rest_countries(db: Session = Depends(get_db)):
    """Admin endpoint - sync data from REST Countries API"""
    from ...scrapers.rest_countries import sync_countries

    result = await sync_countries(db)
    return result

@router.post("/sync-exchange-rates")
async def sync_exchange_rates(db: Session = Depends(get_db)):
    """Admin endpoint - sync currency exchange rates"""
    from ...scrapers.exchange_rates import sync_rates

    result = await sync_rates(db)
    return result

@router.post("/sync-static-info")
async def sync_static_info(db: Session = Depends(get_db)):
    """Admin endpoint - sync static info from JSON"""
    from ...scrapers.static_info import sync_static_data

    result = sync_static_data(db)
    return result

@router.post("/sync-costs")
async def sync_costs_endpoint(db: Session = Depends(get_db)):
    """Admin endpoint - sync cost of living indices"""
    from ...scrapers.costs import sync_costs

    result = sync_costs(db)
    return result

@router.post("/sync-cdc")
async def sync_cdc_endpoint(db: Session = Depends(get_db)):
    """Admin endpoint - sync vaccinations from CDC"""
    from ...scrapers.cdc_health import sync_all_cdc

    result = await sync_all_cdc(db)
    return result

@router.post("/sync-unesco-sites")
async def sync_unesco_sites(db: Session = Depends(get_db)):
    """Admin endpoint - sync UNESCO World Heritage sites"""
    from ...scrapers.attractions import sync_unesco_sites

    result = await sync_unesco_sites(db)
    return result

@router.post("/sync-attractions-wiki")
async def sync_attractions_wiki(db: Session = Depends(get_db)):
    """Admin endpoint - sync top attractions from Wikidata"""
    from ...scrapers.wikidata_attractions import sync_all_wiki_attractions

    result = await sync_all_wiki_attractions(db)
    return result

@router.post("/sync-wiki-summaries")
async def sync_wiki_summaries(db: Session = Depends(get_db)):
    """Admin endpoint - sync country summaries and symbols from Wikipedia/Wikidata"""
    from ...scrapers.wiki_summaries import sync_all_summaries

    result = await sync_all_summaries(db)
    return result

@router.post("/sync-visas")
async def sync_visas_endpoint(db: Session = Depends(get_db)):
    """Admin endpoint - sync detailed visa requirements from Wikipedia"""
    from ...scrapers.visa_wiki import sync_all_visas

    result = await sync_all_visas(db)
    return result

@router.post("/sync-embassies")
async def sync_embassies(db: Session = Depends(get_db)):
    """Admin endpoint - sync Polish embassies and consulates"""
    from ...scrapers.embassies import scrape_embassies

    result = await scrape_embassies(db)
    return result

@router.post("/sync-emergency")
async def sync_emergency(db: Session = Depends(get_db)):
    """Admin endpoint - sync emergency numbers"""
    from ...scrapers.emergency import sync_emergency_numbers

    result = await sync_emergency_numbers(db)
    return result

@router.post("/sync-holidays")
async def sync_holidays_endpoint(db: Session = Depends(get_db)):
    """Admin endpoint - sync public holidays"""
    from ...scrapers.holidays import sync_all_holidays

    result = await sync_all_holidays(db)
    return result

@router.post("/sync-climate")
async def sync_climate_endpoint(force: bool = False, db: Session = Depends(get_db)):
    """Admin endpoint - sync climate data from Open-Meteo"""
    from ...scrapers.climate import sync_all_climate

    result = await sync_all_climate(db, force=force)
    return result

@router.post("/update-all-weather")
async def update_all_weather_endpoint(db: Session = Depends(get_db)):
    """Admin endpoint - update weather for all countries"""
    from ...scrapers.weather import update_all_weather

    result = await update_all_weather(db)
    return result

@router.post("/scrape-msz-gov-pl/{iso_code}")
async def scrape_gov_pl(iso_code: str, db: Session = Depends(get_db)):
    """Admin endpoint - scrape MSZ data for specific country"""
    from ...scrapers.msz_gov_pl import scrape_country

    result = await scrape_country(db, iso_code.upper())
    return result

@router.post("/scrape-all-msz-gov-pl")
async def scrape_all_gov_pl(db: Session = Depends(get_db)):
    """Admin endpoint - scrape data for ALL countries (with rate limiting and slug cache)"""
    from ...scrapers.msz_gov_pl import scrape_all_with_cache

    results = await scrape_all_with_cache(db)
    return results
