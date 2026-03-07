import httpx
from sqlalchemy.orm import Session
from .. import models
from sqlalchemy.sql import func
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List

from .base import BaseScraper

logger = logging.getLogger("uvicorn")

class ExchangeRateScraper(BaseScraper):
    """
    Syncs currency exchange rates from NBP.
    Calculates currency strength based on comparison with historical average (approx 1 year ago).
    """
    def __init__(self, db: Session, concurrency: int = 5, timeout: float = 15.0):
        super().__init__(db, concurrency, timeout)
        self.current_data: Dict[str, Any] = {}
        self.historical_data: Dict[str, float] = {}

    async def run(self, countries: List[models.Country] = None) -> Dict[str, int]:
        """
        Overridden run to fetch all rates once and then sync all currencies.
        """
        urls = [
            "https://api.nbp.pl/api/exchangerates/tables/A?format=json",
            "https://api.nbp.pl/api/exchangerates/tables/B?format=json"
        ]
        
        historical_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
        hist_urls = [
            f"https://api.nbp.pl/api/exchangerates/tables/A/{historical_date}?format=json",
            f"https://api.nbp.pl/api/exchangerates/tables/B/{historical_date}?format=json"
        ]

        async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
            self.client = client
            # Fetch Current
            for url in urls:
                try:
                    resp = await self.client.get(url)
                    if resp.status_code == 200:
                        rates = resp.json()[0].get("rates", [])
                        for r in rates:
                            self.current_data[r["code"].upper()] = {"rate": r["mid"], "name": r["currency"]}
                except Exception as e:
                    logger.warning(f"Error fetching current rates from {url}: {e}")
                    
            # Fetch Historical (Best effort)
            for url in hist_urls:
                try:
                    resp = await self.client.get(url)
                    if resp.status_code == 200:
                        rates = resp.json()[0].get("rates", [])
                        for r in rates:
                            self.historical_data[r["code"].upper()] = r["mid"]
                except Exception as e:
                    logger.warning(f"Error fetching historical rates from {url}: {e}")

        if not self.current_data:
            return {"success": 0, "errors": 1}

        # Instead of countries, we sync all currencies
        updated = 0
        errors = 0
        currencies = self.db.query(models.Currency).all()
        
        for curr in currencies:
            try:
                res = await self.sync_currency(curr)
                if res.get("status") == "success":
                    updated += 1
                else:
                    # Not really an error if it was skipped
                    pass
            except Exception as e:
                logger.error(f"Error syncing currency {curr.code}: {e}")
                errors += 1
        
        return {"success": updated, "errors": errors}

    async def sync_country(self, country: models.Country) -> Any:
        """
        Not used for this scraper as it's currency-centric, 
        but implemented to satisfy BaseScraper.
        """
        return {"status": "skipped", "reason": "Use sync_currency or run()"}

    async def sync_currency(self, curr: models.Currency) -> Any:
        code = curr.code.upper()
        if code in self.current_data:
            info = self.current_data[code]
            curr.exchange_rate_pln = info["rate"]
            curr.name = info["name"].capitalize()
            curr.last_updated = func.now()
            
            # Strength Logic: Is PLN stronger or weaker than a year ago?
            hist_rate = self.historical_data.get(code)
            if hist_rate:
                diff_pct = ((info["rate"] - hist_rate) / hist_rate) * 100
                if diff_pct > 5:
                    curr.relative_cost = "Waluta mocna (droga)"
                elif diff_pct < -5:
                    curr.relative_cost = "Waluta słaba (tania)"
                else:
                    curr.relative_cost = "Kurs stabilny"
            else:
                # Nominal fallback if no history
                if info["rate"] > 10: curr.relative_cost = "Wysoka wartość jedn."
                elif info["rate"] < 0.1: curr.relative_cost = "Niska wartość jedn."
                else: curr.relative_cost = "Średnia"
                
            self.db.commit()
            return {"status": "success"}
        
        return {"status": "skipped", "reason": f"No rate for {code}"}

async def sync_rates(db: Session):
    """
    Legacy wrapper for syncing exchange rates.
    """
    scraper = ExchangeRateScraper(db)
    results = await scraper.run()
    return {"success": results["success"]}
