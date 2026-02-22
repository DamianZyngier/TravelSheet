import httpx
import xml.etree.ElementTree as ET
from sqlalchemy.orm import Session
from .. import models
import asyncio

async def sync_unesco_sites(db: Session):
    """Fetch UNESCO World Heritage Sites from official XML dataset"""
    
    url = "https://whc.unesco.org/en/list/xml/"
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            response = await client.get(url)
            response.raise_for_status()
        except Exception as e:
            return {"error": f"Failed to fetch UNESCO data: {str(e)}"}

    root = ET.fromstring(response.text)
    
    # We will map UNESCO country names to ISO codes (if possible)
    # The XML has <iso_code> for each site (e.g. th, fr, pl)
    
    sites_synced = 0
    for row in root.findall('row'):
        iso_codes = row.find('iso_code').text
        if not iso_codes:
            continue
            
        # ISO codes can be comma separated (multi-country sites)
        iso_list = [i.strip().upper() for i in iso_codes.split(',')]
        
        name = row.find('site').text
        description = row.find('short_description').text if row.find('short_description') is not None else None
        category = row.find('category').text # Cultural, Natural, Mixed
        
        for iso in iso_list:
            country = db.query(models.Country).filter(models.Country.iso_alpha2 == iso).first()
            if not country:
                continue
                
            # Check if exists
            existing = db.query(models.Attraction).filter(
                models.Attraction.country_id == country.id,
                models.Attraction.name == name
            ).first()
            
            if not existing:
                attraction = models.Attraction(
                    country_id=country.id,
                    name=name,
                    description=description,
                    category=category,
                    is_must_see=True,
                    is_unique=True
                )
                db.add(attraction)
                sites_synced += 1
    
    db.commit()
    return {"status": "success", "synced": sites_synced}
