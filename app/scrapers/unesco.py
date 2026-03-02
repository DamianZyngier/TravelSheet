import httpx
from sqlalchemy.orm import Session
from .. import models
import logging
import json
import os
import re
import asyncio
from sqlalchemy.sql import func

logger = logging.getLogger("uvicorn")

# UNESCO Open Data API v2.1
UNESCO_API_BASE_URL = "https://data.unesco.org/api/explore/v2.1/catalog/datasets/whc001/records"
FIELDS = "name_en,short_description_en,date_inscribed,danger,category,states_names,iso_codes,main_image_url,id_no"

def clean_html(text):
    if not text: return ""
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text).strip()

async def fetch_all_unesco_records():
    """Fetch all records from UNESCO Open Data API"""
    all_results = []
    limit = 100
    offset = 0
    total_count = None
    
    headers = {
        "User-Agent": "TravelSheet-App/1.0",
        "Accept": "application/json"
    }

    async with httpx.AsyncClient(timeout=60.0, follow_redirects=True) as client:
        while total_count is None or offset < total_count:
            url = f"{UNESCO_API_BASE_URL}?select={FIELDS}&limit={limit}&offset={offset}&lang=en"
            logger.info(f"Fetching UNESCO API: offset={offset}...")
            
            try:
                resp = await client.get(url, headers=headers)
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
                await asyncio.sleep(0.2)
            except Exception as e:
                logger.error(f"Error at offset {offset}: {e}")
                break
                
    return all_results

def parse_unesco_records(records):
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

async def sync_unesco_sites(db: Session):
    """Main entry point to sync UNESCO data from API to Database"""
    synced_sites = 0
    synced_countries = 0
    errors = 0
    
    records = await fetch_all_unesco_records()
    
    if not records:
        logger.warning("UNESCO API returned no records. Sync aborted.")
        return {"success": 0, "errors": 1}

    unesco_data_dict = parse_unesco_records(records)
    
    # Save a copy as fallback/audit file
    fallback_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'unesco_fallback.json')
    try:
        os.makedirs(os.path.dirname(fallback_path), exist_ok=True)
        with open(fallback_path, 'w', encoding='utf-8') as f:
            json.dump(unesco_data_dict, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Could not save backup file: {e}")

    # Update Database
    for iso, sites in unesco_data_dict.items():
        country = db.query(models.Country).filter(models.Country.iso_alpha2 == iso).first()
        if not country: continue
        
        try:
            db.query(models.UnescoPlace).filter(models.UnescoPlace.country_id == country.id).delete()
            country.unesco_count = len(sites)
            
            for site in sites:
                db.add(models.UnescoPlace(
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
                synced_sites += 1
            synced_countries += 1
        except Exception as e:
            logger.error(f"DB Error for {iso}: {e}")
            errors += 1

    db.commit()
    return {
        "success": synced_countries, 
        "errors": errors,
        "sites_synced": synced_sites
    }
