import httpx
from sqlalchemy.orm import Session
from .. import models
import asyncio
import logging
from typing import Any, List

from .base import BaseScraper
from .utils import async_sparql_get

logger = logging.getLogger("uvicorn")
# Wyciszenie logów HTTPX
logging.getLogger("httpx").setLevel(logging.WARNING)

class WikiAttractionsScraper(BaseScraper):
    """
    Syncs attractions for countries from Wikidata using SPARQL.
    """
    def __init__(self, db: Session, concurrency: int = 1, timeout: float = 90.0):
        # Use low concurrency (1) as Wikidata often struggles with many parallel SPARQL queries
        super().__init__(db, concurrency, timeout)

    async def sync_country(self, country: models.Country) -> Any:
        iso = country.iso_alpha2.upper()
        
        # Optimized query structure for WDQS
        query = f"""
        SELECT DISTINCT ?itemLabel WHERE {{
          ?country wdt:P297 "{iso}".
          ?item wdt:P17 ?country.
          ?item wdt:P31/wdt:P279* wd:Q570116.
          ?item wikibase:sitelinks ?sitelinks.
          FILTER(?sitelinks > 50)
          SERVICE wikibase:label {{ bd:serviceParam wikibase:language "pl,en". }}
        }}
        LIMIT 20
        """

        try:
            results = await async_sparql_get(query, f"Wiki Attractions {iso}")
            if not results:
                return {"status": "skipped", "reason": "No attractions found"}
            
            count = 0
            for res in results:
                if count >= 5: break
                
                name = res.get("itemLabel", {}).get("value")
                if not name or name.startswith("Q"): continue

                existing = self.db.query(models.Attraction).filter(
                    models.Attraction.country_id == country.id,
                    models.Attraction.name == name
                ).first()
                
                if not existing:
                    self.db.add(models.Attraction(
                        country_id=country.id,
                        name=name,
                        category='Wiki Attraction',
                        is_must_see=True,
                        is_unique=False
                    ))
                    count += 1
                else:
                    from sqlalchemy.sql import func
                    existing.last_updated = func.now()
            
            self.db.commit()
            return {"status": "success", "added_count": count}
        except Exception as e:
            logger.error(f"Error syncing attractions for {iso}: {e}")
            return {"error": str(e)}

async def sync_wiki_attractions_batch(db: Session, countries: list[models.Country]):
    """Legacy wrapper for batch sync. Now uses WikiAttractionsScraper for each country."""
    scraper = WikiAttractionsScraper(db)
    for country in countries:
        await scraper.sync_country(country)
        await asyncio.sleep(0.5)

async def sync_all_wiki_attractions(db: Session):
    """Legacy wrapper for syncing all attractions."""
    scraper = WikiAttractionsScraper(db, concurrency=1)
    countries = db.query(models.Country).all()
    results = await scraper.run(countries)
    return {"success": results["success"], "errors": results["errors"]}
