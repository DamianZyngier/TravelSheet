import json
import os
from sqlalchemy.orm import Session
from .. import models

def sync_static_data(db: Session):
    """Load static data from JSON into DB"""
    
    file_path = os.path.join(os.path.dirname(__file__), '../../data/static_data.json')
    if not os.path.exists(file_path):
        return {"error": "File not found"}

    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    synced = 0
    for iso2, info in data.items():
        country = db.query(models.Country).filter(models.Country.iso_alpha2 == iso2).first()
        if not country:
            continue

        practical = db.query(models.PracticalInfo).filter(models.PracticalInfo.country_id == country.id).first()
        
        # Prepare data - join lists to strings for SQLite compatibility
        if "plug_types" in info and isinstance(info["plug_types"], list):
            info["plug_types"] = ",".join(info["plug_types"])

        if practical:
            for key, value in info.items():
                setattr(practical, key, value)
        else:
            practical = models.PracticalInfo(country_id=country.id, **info)
            db.add(practical)
        
        synced += 1

    db.commit()
    return {"synced": synced}
