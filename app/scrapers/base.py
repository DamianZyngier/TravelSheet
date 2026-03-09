import asyncio
import logging
import httpx
import random
from sqlalchemy.orm import Session
from abc import ABC, abstractmethod
from typing import List, Any, Dict, Optional, Type, List, Dict
from .. import models
from .utils import get_headers

logger = logging.getLogger("uvicorn")

class BaseScraper(ABC):
    """
    Base class for all scrapers to provide unified concurrency control, 
    error handling, retry logic, and database session management.
    """
    def __init__(self, db: Session, concurrency: int = 5, timeout: float = 30.0, max_retries: int = 3):
        self.db = db
        self.semaphore = asyncio.Semaphore(concurrency)
        self.timeout = timeout
        self.max_retries = max_retries
        self.client: Optional[httpx.AsyncClient] = None
        # Optional per-request delay to help with rate limiting
        self.rate_limit_delay = 0.2 

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
        
        async with httpx.AsyncClient(
            timeout=self.timeout, 
            follow_redirects=True,
            headers=get_headers()
        ) as client:
            self.client = client
            tasks = [self._limited_sync(country, results) for country in countries]
            await asyncio.gather(*tasks)
            
        return results

    async def _limited_sync(self, country: models.Country, results: Dict[str, int]):
        """
        Internal wrapper to enforce concurrency limits and handle exceptions with retries.
        """
        async with self.semaphore:
            attempt = 0
            while attempt <= self.max_retries:
                try:
                    res = await self.sync_country(country)
                    
                    if isinstance(res, dict) and "error" in res:
                        error_msg = str(res['error'])
                        
                        # Handle specific rate limiting codes
                        if "429" in error_msg or "too many requests" in error_msg.lower():
                            raise httpx.HTTPStatusError("Rate limited (429)", request=None, response=None)
                            
                        logger.error(f"Sync error for {country.iso_alpha2}: {error_msg}")
                        results["errors"] += 1
                        return # Permanent error for this country
                    else:
                        results["success"] += 1
                        return # Success!
                        
                except (httpx.RequestError, httpx.HTTPStatusError) as e:
                    attempt += 1
                    if attempt > self.max_retries:
                        logger.error(f"Failed {country.iso_alpha2} after {self.max_retries} retries: {str(e)}")
                        results["errors"] += 1
                        return
                    
                    # Exponential backoff with jitter
                    wait_time = (2 ** attempt) + random.uniform(0, 1)
                    logger.warning(f"Retry {attempt}/{self.max_retries} for {country.iso_alpha2} due to: {str(e)}. Waiting {wait_time:.1f}s")
                    await asyncio.sleep(wait_time)
                    
                except Exception as e:
                    logger.error(f"Unexpected exception for {country.iso_alpha2}: {type(e).__name__} - {str(e)}")
                    results["errors"] += 1
                    return
                finally:
                    # Small delay to prevent overwhelming external APIs
                    await asyncio.sleep(self.rate_limit_delay)

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
