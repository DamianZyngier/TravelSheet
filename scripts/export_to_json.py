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
    print("Eksportuję dane (Optimized Eager Loading Mode - Extended)...")
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
        
        # Maps for parent names
        id_to_iso = {c.id: c.iso_alpha2 for c in countries}
        id_to_name_pl = {c.id: (c.name_pl or c.name) for c in countries}
        
        output = {}
        for i, c in enumerate(countries):
            # Basic fields mapping
            processed_data = {
                "name": c.name,
                "name_pl": c.name_pl or c.name,
                "iso2": c.iso_alpha2,
                "iso3": c.iso_alpha3,
                "capital": c.capital_pl or c.capital,
                "continent": c.continent,
                "region": c.region,
                "flag_emoji": c.flag_emoji,
                "flag_url": c.flag_url,
                "population": c.population,
                "area": float(c.area) if c.area else None,
                "timezone": c.timezone,
                "national_dish": c.national_dish,
                "wiki_summary": c.wiki_summary,
                "national_symbols": c.national_symbols,
                "unique_animals": c.unique_animals,
                "unique_things": c.unique_things,
                "alcohol_status": c.alcohol_status,
                "lgbtq_status": c.lgbtq_status,
                "id_requirement": c.id_requirement,
                "main_airport": c.main_airport,
                "railway_info": c.railway_info,
                "natural_hazards": c.natural_hazards,
                "popular_apps": c.popular_apps,
                "phone_code": c.phone_code,
                "largest_cities": c.largest_cities,
                "ethnic_groups": c.ethnic_groups,
                "latitude": float(c.latitude) if c.latitude else None,
                "longitude": float(c.longitude) if c.longitude else None,
                "unesco_count": c.unesco_count or 0,
                "is_independent": bool(c.is_independent),
                "last_updated": str(c.updated_at) if c.updated_at else None
            }
            
            # Parent & Territories
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
            
            # Lists
            processed_data["religions"] = [{"name": r.name, "percentage": float(r.percentage)} for r in c.religions]
            processed_data["languages"] = [{"name": l.name, "is_official": l.is_official} for l in c.languages]
            
            # Safety
            if c.safety:
                processed_data["safety"] = {
                    "risk_level": c.safety.risk_level or "unknown",
                    "risk_text": c.safety.summary or "Brak danych",
                    "risk_details": c.safety.risk_details or "",
                    "url": c.safety.full_url or "",
                    "last_updated": str(c.safety.last_checked) if c.safety.last_checked else None
                }
            else:
                processed_data["safety"] = {"risk_level": "unknown", "risk_text": "Brak danych", "risk_details": "", "url": "", "last_updated": None}
            
            # Currency
            if c.currency:
                processed_data["currency"] = {
                    "code": c.currency.code,
                    "name": c.currency.name or "",
                    "rate_pln": float(c.currency.exchange_rate_pln) if c.currency.exchange_rate_pln else None,
                    "last_updated": str(c.currency.last_updated) if c.currency.last_updated else None
                }
            else:
                processed_data["currency"] = {"code": "", "name": "", "rate_pln": None, "last_updated": None}
            
            # Practical
            if c.practical:
                processed_data["practical"] = {
                    "plug_types": c.practical.plug_types or "",
                    "voltage": c.practical.voltage,
                    "water_safe": c.practical.tap_water_safe,
                    "water_safe_for_brushing": c.practical.water_safe_for_brushing,
                    "driving_side": c.practical.driving_side or "right",
                    "card_acceptance": c.practical.card_acceptance or "",
                    "best_exchange_currency": c.practical.best_exchange_currency or "",
                    "exchange_where": c.practical.exchange_where or "",
                    "atm_advice": c.practical.atm_advice or "",
                    "tipping_culture": c.practical.tipping_culture or "",
                    "drinking_age": c.practical.drinking_age or "",
                    "alcohol_rules": c.practical.alcohol_rules or "",
                    "dress_code": c.practical.dress_code or "",
                    "photography_restrictions": c.practical.photography_restrictions or "",
                    "sensitive_topics": c.practical.sensitive_topics or "",
                    "local_norms": c.practical.local_norms or "",
                    "emergency": json.loads(c.practical.emergency_numbers) if c.practical.emergency_numbers else None,
                    "vaccinations_required": c.practical.vaccinations_required or "",
                    "vaccinations_suggested": c.practical.vaccinations_suggested or "",
                    "health_info": c.practical.health_info or "",
                    "roaming_info": c.practical.roaming_info or "",
                    "license_type": c.practical.license_type or "",
                    "last_updated": str(c.practical.last_updated) if c.practical.last_updated else None
                }
            else:
                processed_data["practical"] = {
                    "plug_types": "", "voltage": None, "water_safe": None, "water_safe_for_brushing": None,
                    "driving_side": "right", "card_acceptance": "", "best_exchange_currency": "", 
                    "exchange_where": "", "atm_advice": "", "tipping_culture": "", "drinking_age": "",
                    "alcohol_rules": "", "dress_code": "", "photography_restrictions": "",
                    "sensitive_topics": "", "local_norms": "", "emergency": None, 
                    "vaccinations_required": "", "vaccinations_suggested": "", 
                    "health_info": "", "roaming_info": "", "license_type": "", "last_updated": None
                }

            # Costs
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
                    "daily_budget_high": float(c.costs.daily_budget_high) if c.costs.daily_budget_high else None,
                    "last_updated": str(c.costs.last_updated) if c.costs.last_updated else None
                }
            else:
                processed_data["costs"] = None

            # Entry
            if c.entry_req:
                processed_data["entry"] = {
                    "visa_required": c.entry_req.visa_required,
                    "visa_status": c.entry_req.visa_status or "",
                    "passport_required": c.entry_req.passport_required if c.entry_req.passport_required is not None else True,
                    "temp_passport_allowed": c.entry_req.temp_passport_allowed if c.entry_req.temp_passport_allowed is not None else True,
                    "id_card_allowed": c.entry_req.id_card_allowed if c.entry_req.id_card_allowed is not None else False,
                    "visa_notes": c.entry_req.visa_notes or ""
                }
            else:
                processed_data["entry"] = None
                
            # Weather
            if c.weather:
                processed_data["weather"] = {
                    "temp": float(c.weather.temp_c) if c.weather.temp_c else None,
                    "condition": c.weather.condition or "",
                    "icon": c.weather.condition_icon or "",
                    "forecast": json.loads(c.weather.forecast_json) if c.weather.forecast_json else [],
                    "last_updated": str(c.weather.last_updated) if c.weather.last_updated else None
                }
            else:
                processed_data["weather"] = None

            # Embassies
            processed_data["embassies"] = [
                {
                    "type": e.type,
                    "city": e.city,
                    "address": e.address,
                    "phone": e.phone,
                    "email": e.email,
                    "website": e.website
                } for e in c.embassies
            ]

            # UNESCO
            processed_data["unesco_places"] = [
                {
                    "name": u.name,
                    "category": u.category,
                    "is_danger": bool(u.is_danger),
                    "is_transnational": bool(u.is_transnational),
                    "unesco_id": u.unesco_id,
                    "image_url": u.image_url,
                    "description": u.description
                } for u in c.unesco_places
            ]

            # Attractions
            processed_data["attractions"] = [
                {
                    "name": a.name, 
                    "category": a.category,
                    "description": a.description,
                    "booking_info": a.booking_info
                } for a in c.attractions[:15]
            ]
            
            # Holidays
            processed_data["holidays"] = [{"name": h.name, "date": str(h.date)} for h in c.holidays]
            
            # Climate
            processed_data["climate"] = [
                {
                    "month": cl.month,
                    "temp_day": cl.avg_temp_max,
                    "temp_night": cl.avg_temp_min,
                    "rain": cl.avg_rain_mm
                } for cl in c.climate
            ]

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
