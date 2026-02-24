import httpx
from sqlalchemy.orm import Session
from .. import models
import json
import logging
import asyncio

logger = logging.getLogger("uvicorn")

# Robust manual mapping for major countries
MANUAL_FALLBACKS = {
    'US': {"police": "911", "ambulance": "911", "fire": "911", "dispatch": "911", "member_112": False},
    'CA': {"police": "911", "ambulance": "911", "fire": "911", "dispatch": "911", "member_112": False},
    'GB': {"police": "999", "ambulance": "999", "fire": "999", "dispatch": "112", "member_112": True},
    'AU': {"police": "000", "ambulance": "000", "fire": "000", "dispatch": "112", "member_112": True},
    'NZ': {"police": "111", "ambulance": "111", "fire": "111", "dispatch": "111", "member_112": False},
    'JP': {"police": "110", "ambulance": "119", "fire": "119", "dispatch": "", "member_112": False},
    'KR': {"police": "112", "ambulance": "119", "fire": "119", "dispatch": "", "member_112": False},
    'DE': {"police": "110", "ambulance": "112", "fire": "112", "dispatch": "112", "member_112": True},
    'FR': {"police": "17", "ambulance": "15", "fire": "18", "dispatch": "112", "member_112": True},
    'IT': {"police": "113", "ambulance": "118", "fire": "115", "dispatch": "112", "member_112": True},
    'ES': {"police": "091", "ambulance": "061", "fire": "080", "dispatch": "112", "member_112": True},
    'PL': {"police": "997", "ambulance": "999", "fire": "998", "dispatch": "112", "member_112": True},
}

async def sync_emergency_numbers(db: Session):
    countries = db.query(models.Country).all()
    results = {"synced": 0, "errors": 0}
    
    dump_data = {}
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get("https://emergencynumberapi.com/api/data/all")
            if resp.status_code == 200:
                data = resp.json()
                full_list = data.get("value", data) if isinstance(data, dict) else data
                if isinstance(full_list, list):
                    for entry in full_list:
                        iso = entry.get("Country", {}).get("ISOCode")
                        if iso: dump_data[iso.upper()] = entry
    except Exception as e:
        logger.warning(f"Dump error: {e}")

    for country in countries:
        iso2 = country.iso_alpha2.upper()
        emergency_data = None
        
        if iso2 in dump_data:
            d = dump_data[iso2]
            def extract(cat):
                obj = d.get(cat, {})
                val = None
                if isinstance(obj, dict):
                    val = obj.get("All") or obj.get("Fixed") or obj.get("GSM")
                elif isinstance(obj, list):
                    val = obj[0] if obj else None
                else:
                    val = obj
                
                # If we got a list from 'All' etc.
                if isinstance(val, list):
                    val = val[0] if val else None
                return str(val).strip() if val else None

            emergency_data = {
                "police": extract("Police"),
                "ambulance": extract("Ambulance"),
                "fire": extract("Fire"),
                "dispatch": extract("Dispatch"),
                "member_112": d.get("Member_112") is True or d.get("Member_112") == "true"
            }

        # Fallback
        if not emergency_data or all(not emergency_data.get(k) for k in ["police", "ambulance", "fire"]):
            if iso2 in MANUAL_FALLBACKS:
                emergency_data = MANUAL_FALLBACKS[iso2]

        if emergency_data:
            # Clean values
            for k in ["police", "ambulance", "fire", "dispatch"]:
                if not emergency_data[k] or emergency_data[k].lower() == "none" or emergency_data[k] == "null":
                    emergency_data[k] = None

            try:
                practical = db.query(models.PracticalInfo).filter(models.PracticalInfo.country_id == country.id).first()
                if not practical:
                    practical = models.PracticalInfo(country_id=country.id)
                    db.add(practical)
                practical.emergency_numbers = json.dumps(emergency_data)
                db.commit()
                results["synced"] += 1
            except Exception as e:
                results["errors"] += 1
                
    return results
