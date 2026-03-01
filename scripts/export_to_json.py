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
    print("Eksportuję dane (Optimized Eager Loading Mode)...")
    db = SessionLocal()
    
    try:
        # Fetch all countries with all relationships pre-loaded to avoid N+1 queries
        countries = db.query(models.Country).options(
            selectinload(models.Country.languages),
            selectinload(models.Country.religions),
            selectinload(models.Country.embassies),
            selectinload(models.Country.unesco_places),
            selectinload(models.Country.attractions),
            selectinload(models.Country.holidays),
            selectinload(models.Country.climate),
            selectinload(models.Country.territories),
            joinedload(models.Country.currency),
            joinedload(models.Country.safety),
            joinedload(models.Country.practical),
            joinedload(models.Country.costs),
            joinedload(models.Country.entry_req),
            joinedload(models.Country.weather)
        ).all()
        
        print(f"Pobrano {len(countries)} krajów.")
        
        # Maps for parent names (parent object is already loaded via relationship)
        id_to_iso = {c.id: c.iso_alpha2 for c in countries}
        id_to_name_pl = {c.id: (c.name_pl or c.name) for c in countries}
        
        output = {}
        for i, c in enumerate(countries):
            # Using model_validate from CountryDetail (which is already configured for from_attributes)
            c_schema = schemas.CountryDetail.model_validate(c)
            c_dict = c_schema.model_dump()
            
            # Legacy structure adjustments
            processed_data = c_dict
            processed_data["name_pl"] = c.name_pl or c.name
            processed_data["capital"] = c.capital_pl or c.capital
            processed_data["area"] = float(c.area) if c.area else None
            processed_data["latitude"] = float(c.latitude) if c.latitude else None
            processed_data["longitude"] = float(c.longitude) if c.longitude else None
            
            # Parent & Territories names mapping
            processed_data["parent"] = {
                "iso2": id_to_iso.get(c.parent_id),
                "name_pl": id_to_name_pl.get(c.parent_id)
            } if c.parent_id else None
            
            processed_data["territories"] = [
                {
                    "iso2": t.iso_alpha2,
                    "name_pl": id_to_name_pl.get(t.id)
                } for t in c.territories
            ]
            
            # Dates to string for holidays (Pydantic does this by default but just in case)
            processed_data["holidays"] = [
                {"name": h.name, "date": str(h.date)} for h in c.holidays
            ]
            
            # Safety mapping (legacy field names)
            if c.safety:
                processed_data["safety"] = {
                    "risk_level": c.safety.risk_level or "unknown",
                    "risk_text": c.safety.summary or "Brak danych",
                    "risk_details": c.safety.risk_details or "",
                    "url": c.safety.full_url or ""
                }
            
            # Currency mapping
            if c.currency:
                processed_data["currency"] = {
                    "code": c.currency.code,
                    "name": c.currency.name or "",
                    "rate_pln": float(c.currency.exchange_rate_pln) if c.currency.exchange_rate_pln else None
                }
            
            # Weather mapping
            if c.weather:
                processed_data["weather"] = {
                    "temp": float(c.weather.temp_c) if c.weather.temp_c else None,
                    "condition": c.weather.condition or "",
                    "icon": c.weather.condition_icon or "",
                    "forecast": json.loads(c.weather.forecast_json) if c.weather.forecast_json else []
                }

            # Climate mapping
            processed_data["climate"] = [
                {
                    "month": cl.month,
                    "temp_day": cl.avg_temp_max,
                    "temp_night": cl.avg_temp_min,
                    "rain": cl.avg_rain_mm
                } for cl in c.climate
            ]

            # Costs (convert decimals to float)
            if c.costs:
                processed_data["costs"] = {
                    "index": float(c.costs.index_overall) if c.costs.index_overall else None,
                    "restaurants": float(c.costs.index_restaurants) if c.costs.index_restaurants else None,
                    "groceries": float(c.costs.index_groceries) if c.costs.index_groceries else None,
                    "transport": float(c.costs.index_transport) if c.costs.index_transport else None,
                    "accommodation": float(c.costs.index_accommodation) if c.costs.index_accommodation else None,
                    "ratio_to_pl": float(c.costs.ratio_to_poland) if c.costs.ratio_to_poland else None,
                    "daily_budget_low": float(c.costs.daily_budget_low) if c.costs.daily_budget_low else None,
                    "daily_budget_mid": float(c.costs.daily_budget_mid) if c.costs.daily_budget_mid else None,
                    "daily_budget_high": float(c.costs.daily_budget_high) if c.costs.daily_budget_high else None
                }

            output[c.iso_alpha2] = processed_data
            if (i+1) % 100 == 0:
                print(f"Przetworzono {i+1}/{len(countries)} krajów...")

        # Save to files
        json_path = os.environ.get('JSON_OUTPUT_PATH', 'docs/data.json')
        os.makedirs(os.path.dirname(json_path), exist_ok=True)
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)

        if 'JSON_OUTPUT_PATH' not in os.environ:
            os.makedirs('frontend/public', exist_ok=True)
            with open('frontend/public/data.json', 'w', encoding='utf-8') as f:
                json.dump(output, f, ensure_ascii=False, indent=2)

        print(f"Eksport zakończony sukcesem! data.json zawiera {len(output)} krajów.")

    finally:
        db.close()

if __name__ == "__main__":
    export_all()
