import json
import os
import sys
from sqlalchemy.orm import Session, selectinload, joinedload
from sqlalchemy import create_engine

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app import models, schemas

def export_all():
    print("Eksportuję dane (Optimized Pydantic Export Mode)...")
    db = SessionLocal()
    
    try:
        # Fetch all countries with all relationships pre-loaded for performance
        countries = db.query(models.Country).options(
            selectinload(models.Country.languages),
            selectinload(models.Country.religions),
            selectinload(models.Country.embassies),
            selectinload(models.Country.unesco_places),
            selectinload(models.Country.attractions),
            selectinload(models.Country.holidays),
            selectinload(models.Country.climate),
            selectinload(models.Country.territories),
            selectinload(models.Country.laws_and_customs),
            selectinload(models.Country.souvenirs),
            joinedload(models.Country.currency).selectinload(models.Currency.denominations),
            joinedload(models.Country.safety),
            joinedload(models.Country.practical),
            joinedload(models.Country.costs),
            joinedload(models.Country.entry_req),
            joinedload(models.Country.weather)
        ).all()
        
        print(f"Pobrano {len(countries)} krajów.")
        
        # Pre-compute helper maps for parent/territory names
        id_to_iso = {c.id: c.iso_alpha2 for c in countries}
        id_to_name_pl = {c.id: (c.name_pl or c.name) for c in countries}
        
        output = {}
        for i, c in enumerate(countries):
            # Prepare data for Pydantic validation
            # We map some non-standard DB names to schema names here if they differ
            
            export_data = {
                **c.__dict__,
                "iso2": c.iso_alpha2,
                "iso3": c.iso_alpha3,
                "capital": c.capital,
                "last_updated": c.updated_at,
                "parent": {"iso2": id_to_iso.get(c.parent_id), "name_pl": id_to_name_pl.get(c.parent_id)} if c.parent_id else None,
                "territories": [{"iso2": t.iso_alpha2, "name_pl": id_to_name_pl.get(t.id)} for t in c.territories],
                "religions": [{"name": r.name, "percentage": r.percentage, "last_updated": str(r.last_updated)} for r in c.religions],
                "languages": [{"name": l.name, "is_official": l.is_official, "last_updated": str(l.last_updated)} for l in c.languages],
                
                "safety": {
                    "risk_level": c.safety.risk_level if c.safety else "unknown",
                    "is_partial": c.safety.is_partial if c.safety else False,
                    "risk_text": c.safety.summary if c.safety else "Brak danych.",
                    "risk_details": c.safety.risk_details if c.safety else "",
                    "url": c.safety.full_url if c.safety else "",
                    "last_updated": str(c.safety.last_checked) if c.safety else None
                },
                
                "currency": {
                    "code": c.currency.code if c.currency else "",
                    "name": c.currency.name if c.currency else "",
                    "rate_pln": float(c.currency.exchange_rate_pln) if c.currency and c.currency.exchange_rate_pln else None,
                    "relative_cost": c.currency.relative_cost if c.currency else None,
                    "last_updated": str(c.currency.last_updated) if c.currency else None,
                    "denominations": [{"value": d.value, "type": d.type, "image_url": d.image_url} for d in c.currency.denominations] if c.currency else []
                },
                
                "practical": c.practical, # Pydantic will handle this from attributes
                
                "costs": {
                    "index": float(c.costs.index_overall) if c.costs and c.costs.index_overall else None,
                    "restaurants": float(c.costs.index_restaurants) if c.costs and c.costs.index_restaurants else None,
                    "groceries": float(c.costs.index_groceries) if c.costs and c.costs.index_groceries else None,
                    "transport": float(c.costs.index_transport) if c.costs and c.costs.index_transport else None,
                    "accommodation": float(c.costs.index_accommodation) if c.costs and c.costs.index_accommodation else None,
                    "ratio_to_pl": float(c.costs.ratio_to_poland) if c.costs and c.costs.ratio_to_poland else None,
                    "daily_budget_low": float(c.costs.daily_budget_low) if c.costs and c.costs.daily_budget_low else None,
                    "daily_budget_mid": float(c.costs.daily_budget_mid) if c.costs and c.costs.daily_budget_mid else None,
                    "daily_budget_high": float(c.costs.daily_budget_high) if c.costs and c.costs.daily_budget_high else None,
                    "last_updated": str(c.costs.last_updated) if c.costs else None
                } if c.costs else None,
                
                "entry": {
                    "visa_required": bool(c.entry_req.visa_required),
                    "visa_status": c.entry_req.visa_status,
                    "passport_required": bool(c.entry_req.passport_required),
                    "temp_passport_allowed": bool(c.entry_req.temp_passport_allowed),
                    "id_card_allowed": bool(c.entry_req.id_card_allowed),
                    "visa_notes": c.entry_req.visa_notes,
                    "last_updated": str(c.entry_req.last_updated)
                } if c.entry_req else None,
                
                "weather": {
                    "temp": float(c.weather.temp_c) if c.weather and c.weather.temp_c else None,
                    "condition": c.weather.condition if c.weather else "",
                    "icon": c.weather.condition_icon if c.weather else "",
                    "forecast": c.weather.forecast_json if c.weather else "[]",
                    "last_updated": str(c.weather.last_updated) if c.weather else None
                } if c.weather else None,
                
                "souvenirs_list": [{"name": s.name, "description": s.description, "category": s.category, "image_url": s.image_url} for s in c.souvenirs],
                "unesco_places": [
                    {
                        "name": u.name, "category": u.category, "is_danger": bool(u.is_danger), 
                        "is_transnational": bool(u.is_transnational), "unesco_id": u.unesco_id, 
                        "image_url": u.image_url, "description": u.description, "last_updated": str(u.last_updated)
                    } for u in c.unesco_places
                ],
                "attractions": [{"name": a.name, "category": a.category, "description": a.description, "last_updated": str(a.last_updated)} for a in c.attractions[:15]],
                "holidays": [{"name": h.name, "date": str(h.date), "last_updated": str(h.last_updated)} for h in c.holidays],
                "climate": [{"month": cl.month, "temp_day": cl.avg_temp_max, "temp_night": cl.avg_temp_min, "rain": cl.avg_rain_mm, "season": cl.season_type, "last_updated": str(cl.last_updated)} for cl in c.climate],
                "laws_and_customs": [{"category": lc.category, "title": lc.title, "description": lc.description, "last_updated": str(lc.last_updated)} for lc in c.laws_and_customs],
                "embassies": [
                    {
                        "type": e.type, "city": e.city, "address": e.address, "phone": e.phone, 
                        "emergency_phone": e.emergency_phone, "email": e.email, "website": e.website, "last_updated": str(e.last_updated)
                    } for e in c.embassies
                ]
            }
            
            # Validate and clean with Pydantic
            validated = schemas.CountryExportSchema.model_validate(export_data)
            output[c.iso_alpha2] = validated.model_dump(mode='json')
            
            if (i+1) % 100 == 0:
                print(f"Przetworzono {i+1}/{len(countries)} krajów...")

        with open('docs/data.json', 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        print(f"Eksport zakończony sukcesem! data.json zawiera {len(output)} krajów.")
    finally:
        db.close()

if __name__ == "__main__":
    export_all()
