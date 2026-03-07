import asyncio
import logging
import httpx
from sqlalchemy.orm import Session
from abc import ABC, abstractmethod
from typing import List, Any, Dict, Optional, Type
from .. import models
from .utils import get_headers

logger = logging.getLogger("uvicorn")

class BaseScraper(ABC):
    """
    Base class for all scrapers to provide unified concurrency control, 
    error handling, and database session management.
    """
    def __init__(self, db: Session, concurrency: int = 5, timeout: float = 30.0):
        self.db = db
        self.semaphore = asyncio.Semaphore(concurrency)
        self.timeout = timeout
        self.client: Optional[httpx.AsyncClient] = None

    @abstractmethod
    async def sync_country(self, country: models.Country) -> Any:
        """
        Logic to sync data for a single country. 
        Must be implemented by subclasses.
        """
        pass

    async def run(self, countries: List[models.Country]) -> Dict[str, int]:
        """
        Orchestrates parallel synchronization for a list of countries.
        """
        results = {"success": 0, "errors": 0}
        
        async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
            self.client = client
            tasks = [self._limited_sync(country, results) for country in countries]
            await asyncio.gather(*tasks)
            
        return results

    async def _limited_sync(self, country: models.Country, results: Dict[str, int]):
        """
        Internal wrapper to enforce concurrency limits and handle exceptions.
        """
        async with self.semaphore:
            try:
                res = await self.sync_country(country)
                if isinstance(res, dict) and "error" in res:
                    logger.error(f"Sync error for {country.iso_alpha2}: {res['error']}")
                    results["errors"] += 1
                else:
                    results["success"] += 1
            except Exception as e:
                logger.error(f"Unexpected exception for {country.iso_alpha2}: {type(e).__name__} - {str(e)}")
                results["errors"] += 1
            finally:
                # Small delay to prevent overwhelming external APIs
                await asyncio.sleep(0.1)

    async def get_or_create(self, model_class: Type, country_id: int) -> Any:
        """
        Helper to fetch an existing related record or create a new one.
        """
        obj = self.db.query(model_class).filter(model_class.country_id == country_id).first()
        if not obj:
            obj = model_class(country_id=country_id)
            self.db.add(obj)
        return obj

    async def parent_fallback(self, country: models.Country, depth: int = 0) -> Any:
        """
        Generic logic to fall back to a parent country if the current one has no data.
        """
        if depth > 1 or not country.parent_id:
            return {"error": "No data found and no further fallbacks available"}
            
        parent = self.db.query(models.Country).get(country.parent_id)
        if parent:
            logger.info(f"Falling back: {country.iso_alpha2} -> {parent.iso_alpha2}")
            return await self.sync_country(parent)
        return {"error": "Parent not found in database"}
