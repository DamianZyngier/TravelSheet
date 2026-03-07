import httpx
import logging
import json
import os
import re
import asyncio
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy.sql import func

from .. import models
from .base import BaseScraper

logger = logging.getLogger("uvicorn")

# UNESCO Open Data API v2.1
UNESCO_API_BASE_URL = "https://data.unesco.org/api/explore/v2.1/catalog/datasets/whc001/records"
FIELDS = "name_en,short_description_en,date_inscribed,danger,category,states_names,iso_codes,main_image_url,id_no"

def clean_html(text):
    if not text: return ""
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text).strip()

class UnescoScraper(BaseScraper):
    """
    Syncs UNESCO World Heritage Sites from UNESCO Open Data API.
    """
    def __init__(self, db: Session, concurrency: int = 5, timeout: float = 60.0):
        super().__init__(db, concurrency, timeout)
        self.unesco_data_dict: Dict[str, List[Dict[str, Any]]] = {}

    async def run(self, countries: List[models.Country]) -> Dict[str, int]:
        """
        Overridden run to fetch all UNESCO records once.
        """
        all_results = []
        limit = 100
        offset = 0
        total_count = None
        
        headers = {
            "User-Agent": "TravelSheet-App/1.0",
            "Accept": "application/json"
        }

        async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
            self.client = client
            while total_count is None or offset < total_count:
                url = f"{UNESCO_API_BASE_URL}?select={FIELDS}&limit={limit}&offset={offset}&lang=en"
                logger.info(f"Fetching UNESCO API: offset={offset}...")
                
                try:
                    resp = await self.client.get(url, headers=headers)
                    if resp.status_code != 200:
                        logger.error(f"UNESCO API error: HTTP {resp.status_code}")
                        break
                    
                    data = resp.json()
                    if total_count is None:
                        total_count = data.get("total_count", 0)
                    
                    results = data.get("results", [])
                    if not results:
                        break
                    
                    all_results.extend(results)
                    offset += len(results)
                    await asyncio.sleep(0.1)
                except Exception as e:
                    logger.error(f"Error at offset {offset}: {e}")
                    break
        
        if not all_results:
            return {"success": 0, "errors": 1}

        self.unesco_data_dict = self._parse_unesco_records(all_results)
        
        # Save a copy as fallback/audit file
        fallback_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'unesco_fallback.json')
        try:
            os.makedirs(os.path.dirname(fallback_path), exist_ok=True)
            with open(fallback_path, 'w', encoding='utf-8') as f:
                json.dump(self.unesco_data_dict, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Could not save backup file: {e}")

        results = {"success": 0, "errors": 0}
        tasks = [self._limited_sync(country, results) for country in countries]
        await asyncio.gather(*tasks)
        
        return results

    def _parse_unesco_records(self, records: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Parse API records into a dictionary indexed by ISO alpha-2 codes"""
        unesco_data_dict = {}
        for rec in records:
            uid = rec.get('id_no')
            danger_val = str(rec.get('danger', '')).lower() == "true"
            
            main_img = rec.get('main_image_url')
            img_url = main_img.get('url') if isinstance(main_img, dict) else None
            
            # Image fallback if not provided by API
            if not img_url and uid:
                img_url = f"https://whc.unesco.org/uploads/sites/gallery/original/site_{str(uid).zfill(4)}_0001.jpg"

            iso_codes_raw = rec.get('iso_codes')
            iso_codes = []
            if iso_codes_raw:
                iso_codes = [c.strip().upper() for c in iso_codes_raw.split(',')]
                
            is_transnational = len(iso_codes) > 1

            site_obj = {
                "name": rec.get('name_en'),
                "category": rec.get('category'),
                "is_danger": danger_val,
                "is_transnational": is_transnational,
                "id": uid,
                "image": img_url,
                "description": clean_html(rec.get('short_description_en'))
            }
            
            if iso_codes:
                for iso in iso_codes:
                    if not iso: continue
                    if iso not in unesco_data_dict:
                        unesco_data_dict[iso] = []
                    unesco_data_dict[iso].append(site_obj)
        return unesco_data_dict

    async def sync_country(self, country: models.Country) -> Any:
        sites = self.unesco_data_dict.get(country.iso_alpha2.upper(), [])
        
        try:
            self.db.query(models.UnescoPlace).filter(models.UnescoPlace.country_id == country.id).delete()
            country.unesco_count = len(sites)
            
            for site in sites:
                self.db.add(models.UnescoPlace(
                    country_id=country.id,
                    unesco_id=str(site["id"]) if site["id"] else None,
                    name=site["name"],
                    category=site["category"],
                    is_danger=site.get("is_danger", False),
                    is_transnational=site.get("is_transnational", False),
                    image_url=site["image"],
                    description=site["description"],
                    last_updated=func.now()
                ))
            
            self.db.commit()
            return {"status": "success", "sites_count": len(sites)}
        except Exception as e:
            logger.error(f"DB Error for {country.iso_alpha2}: {e}")
            return {"error": str(e)}

async def sync_unesco_sites(db: Session):
    """Legacy wrapper for syncing UNESCO sites."""
    scraper = UnescoScraper(db)
    countries = db.query(models.Country).all()
    results = await scraper.run(countries)
    
    # Return count of all sites for legacy compatibility
    synced_sites = db.query(func.count(models.UnescoPlace.id)).scalar()
    results["sites_synced"] = synced_sites
    return results
