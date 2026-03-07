import asyncio
import logging
from sqlalchemy.orm import Session
from sqlalchemy import func
from .. import models
from .utils import async_sparql_get
from .base import BaseScraper

logger = logging.getLogger("uvicorn")

class WikidataInfoScraper(BaseScraper):
    def __init__(self, db: Session):
        # SPARQL is handled by a global semaphore in utils, so concurrency here can be higher for orchestration
        super().__init__(db, concurrency=5, timeout=120.0)

    async def sync_country(self, country: models.Country):
        iso = country.iso_alpha2
        
        # Extended info query
        query = f"""
        SELECT ?prop ?propLabel ?value ?valueLabel WHERE {{
          ?country wdt:P498 "{iso}".
          ?country ?p ?value.
          ?prop wikibase:directClaim ?p.
          SERVICE wikibase:label {{ bd:serviceParam wikibase:language "pl,en". }}
        }}
        """
        
        try:
            results = await async_sparql_get(query, f"Extended Info for {iso}")
            if not results: return {"status": "no_data"}

            # Map important properties
            props = {
                "P421": "timezone",
                "P2093": "national_dish",
                "P1448": "national_symbols",
                "P1082": "population",
                "P2046": "area",
                "P1081": "hdi",
                "P2250": "life_expectancy",
                "P2131": "gdp_nominal",
                "P2132": "gdp_ppp",
                "P3529": "gini",
                "P94": "coat_of_arms_url",
                "P571": "inception_date",
                "P856": "official_tourist_website"
            }

            for row in results:
                p_id = row["prop"]["value"].split("/")[-1]
                if p_id in props:
                    val = row["valueLabel"]["value"]
                    setattr(country, props[p_id], val)

            # Population/Area conversion
            if country.population and isinstance(country.population, str):
                try: country.population = int(float(country.population))
                except: pass
            
            self.db.commit()
            return {"status": "success"}
        except Exception as e:
            return {"error": str(e)}

async def sync_all_wikidata_info(db: Session):
    countries = db.query(models.Country).all()
    scraper = WikidataInfoScraper(db)
    return await scraper.run(countries)
