import logging
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from typing import Any

from .. import models
from .base import BaseScraper

logger = logging.getLogger("uvicorn")

# Cost of Living Index (approximate, base NY = 100)
# Data based on open statistics (Numbeo/World Bank 2024 averages)
COST_DATA = {
    'AF': 25, 'AL': 35, 'DZ': 28, 'AD': 65, 'AO': 45, 'AG': 60, 'AR': 35, 'AM': 32, 'AU': 75, 'AT': 68,
    'AZ': 30, 'BS': 85, 'BH': 55, 'BD': 25, 'BB': 78, 'BY': 30, 'BE': 65, 'BZ': 48, 'BJ': 35, 'BT': 30,
    'BO': 32, 'BA': 35, 'BW': 38, 'BR': 38, 'BN': 50, 'BG': 38, 'BF': 35, 'BI': 25, 'KH': 32, 'CM': 38,
    'CA': 70, 'CV': 42, 'CF': 40, 'TD': 45, 'CL': 45, 'CN': 40, 'CO': 30, 'KM': 35, 'CG': 45, 'CD': 45,
    'CR': 48, 'CI': 42, 'HR': 48, 'CU': 40, 'CY': 55, 'CZ': 45, 'DK': 80, 'DJ': 45, 'DM': 55, 'DO': 45,
    'EC': 38, 'EG': 25, 'SV': 45, 'GQ': 50, 'ER': 45, 'EE': 52, 'SZ': 35, 'ET': 28, 'FJ': 45, 'FI': 72,
    'FR': 70, 'GA': 45, 'GM': 28, 'GE': 32, 'DE': 68, 'GH': 35, 'GR': 55, 'GD': 60, 'GT': 42, 'GN': 38,
    'GW': 35, 'GY': 42, 'HT': 45, 'HN': 40, 'HU': 42, 'IS': 85, 'IN': 25, 'ID': 32, 'IR': 35, 'IQ': 35,
    'IE': 75, 'IL': 75, 'IT': 65, 'JM': 55, 'JP': 65, 'JO': 50, 'KZ': 32, 'KE': 35, 'KI': 55, 'KW': 52,
    'KG': 28, 'LA': 32, 'LV': 48, 'LB': 45, 'LS': 35, 'LR': 42, 'LY': 35, 'LI': 95, 'LT': 48, 'LU': 82,
    'MG': 28, 'MW': 25, 'MY': 38, 'MV': 65, 'ML': 35, 'MT': 60, 'MH': 65, 'MR': 35, 'MU': 45, 'MX': 42,
    'FM': 65, 'MD': 32, 'MC': 95, 'MN': 32, 'ME': 42, 'MA': 35, 'MZ': 35, 'MM': 32, 'NA': 38, 'NR': 65,
    'NP': 25, 'NL': 72, 'NZ': 72, 'NI': 38, 'NE': 35, 'NG': 35, 'NO': 85, 'OM': 50, 'PK': 22, 'PW': 75,
    'PA': 48, 'PG': 55, 'PY': 32, 'PE': 35, 'PH': 35, 'PL': 42, 'PT': 52, 'QA': 65, 'RO': 40, 'RU': 38,
    'RW': 32, 'KN': 75, 'LC': 65, 'VC': 65, 'WS': 55, 'SM': 65, 'ST': 42, 'SA': 52, 'SN': 42, 'RS': 40,
    'SC': 72, 'SL': 32, 'SG': 82, 'SK': 48, 'SI': 52, 'SB': 55, 'SO': 35, 'ZA': 42, 'KR': 65, 'SS': 35,
    'ES': 58, 'LK': 30, 'SD': 35, 'SR': 45, 'SE': 72, 'CH': 98, 'SY': 30, 'TJ': 28, 'TZ': 32, 'TH': 42,
    'TL': 35, 'TG': 35, 'TO': 55, 'TT': 55, 'TN': 30, 'TR': 35, 'TM': 45, 'TV': 65, 'UG': 32, 'UA': 35,
    'AE': 65, 'GB': 70, 'US': 75, 'UY': 55, 'UZ': 30, 'VU': 65, 'VE': 45, 'VN': 35, 'YE': 35, 'ZM': 35, 'ZW': 38
}

class CostsScraper(BaseScraper):
    """
    Updates cost of living based on pre-calculated index data.
    Calculates ratio relative to Poland (PL).
    """
    def __init__(self, db: Session, concurrency: int = 5, timeout: float = 30.0):
        super().__init__(db, concurrency, timeout)
        self.pl_index = COST_DATA.get('PL', 42.0)

    async def sync_country(self, country: models.Country) -> Any:
        index = COST_DATA.get(country.iso_alpha2.upper())
        if not index:
            return {"status": "skipped", "reason": "No cost data available"}
            
        ratio = round(index / self.pl_index, 2)
        pl_low, pl_mid, pl_high = 120.0, 300.0, 800.0
        
        cost_entry = await self.get_or_create(models.CostOfLiving, country.id)
        
        cost_entry.index_overall = index
        cost_entry.index_restaurants = index * 0.95
        cost_entry.index_groceries = index * 1.05
        cost_entry.index_transport = index * 0.85
        cost_entry.index_accommodation = index * 1.2
        cost_entry.ratio_to_poland = ratio
        cost_entry.daily_budget_low = round(pl_low * ratio, 2)
        cost_entry.daily_budget_mid = round(pl_mid * ratio, 2)
        cost_entry.daily_budget_high = round(pl_high * ratio, 2)
        cost_entry.last_updated = func.now()
        
        self.db.commit()
        return {"status": "success"}

def sync_costs(db: Session):
    """
    Legacy wrapper for synchronous sync. 
    Actually runs asynchronously through CostsScraper.
    """
    import asyncio
    scraper = CostsScraper(db)
    countries = db.query(models.Country).all()
    results = asyncio.run(scraper.run(countries))
    logger.info(f"Synced cost data: {results['success']} success, {results['errors']} errors")
    return results
