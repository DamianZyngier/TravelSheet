import httpx
from sqlalchemy.orm import Session
from .. import models
import logging
import json
import os

logger = logging.getLogger("uvicorn")

async def sync_unesco_sites(db: Session):
    """Sync UNESCO sites using static data fallback from json file"""
    synced_sites = 0
    synced_countries = 0
    errors = []
    
    # Path to fallback data
    fallback_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'unesco_fallback.json')
    
    try:
        if not os.path.exists(fallback_path):
            error_msg = f"Fallback file not found at {fallback_path}"
            logger.error(error_msg)
            return {"status": "error", "message": error_msg}

        with open(fallback_path, 'r', encoding='utf-8') as f:
            unesco_fallback = json.load(f)
    except json.JSONDecodeError as e:
        error_msg = f"Failed to parse unesco_fallback.json: {e}"
        logger.error(error_msg)
        return {"status": "error", "message": error_msg}
    except Exception as e:
        error_msg = f"Failed to load unesco_fallback.json: {e}"
        logger.error(error_msg)
        return {"status": "error", "message": error_msg}

    # Process fallback data
    for iso, sites in unesco_fallback.items():
        country = db.query(models.Country).filter(models.Country.iso_alpha2 == iso.upper()).first()
        if not country:
            continue
        
        try:
            # Clear existing unesco places for this country to avoid duplicates on re-run
            db.query(models.UnescoPlace).filter(models.UnescoPlace.country_id == country.id).delete()
            
            # Update total count
            country.unesco_count = len(sites)
            
            # Add all sites
            for site_data in sites:
                name = ""
                category = ""
                uid = None
                img = None
                description = None
                
                if isinstance(site_data, list):
                    name = site_data[0]
                    category = site_data[1]
                else: # Dict format
                    name = site_data.get("name")
                    category = site_data.get("category")
                    uid = site_data.get("id")
                    img = site_data.get("image")
                    description = site_data.get("description")

                db.add(models.UnescoPlace(
                    country_id=country.id,
                    unesco_id=str(uid) if uid else None,
                    name=name,
                    category=category,
                    image_url=img,
                    description=description
                ))
                synced_sites += 1
            
            synced_countries += 1
        except Exception as e:
            err = f"Error syncing {iso}: {str(e)}"
            logger.error(err)
            errors.append(err)
    
    db.commit()
    logger.info(f"UNESCO Sync: Processed {synced_countries} countries, {synced_sites} sites total.")
    if errors:
        logger.warning(f"UNESCO Sync encountered {len(errors)} errors.")

    return {
        "status": "success", 
        "countries_synced": synced_countries, 
        "sites_synced": synced_sites,
        "errors": errors
    }

async def sync_attractions_placeholder(db: Session):
    """
    Placeholder for general attractions (not UNESCO).
    Currently we use Wikidata attractions scraper for this.
    """
    return {"status": "info", "message": "General attractions are synced via Wikidata scraper"}
