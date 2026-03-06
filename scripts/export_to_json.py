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
        # Fetch all countries with all relationships pre-loaded
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
        
        id_to_iso = {c.id: c.iso_alpha2 for c in countries}
        id_to_name_pl = {c.id: (c.name_pl or c.name) for c in countries}
        
        output = {}
        for i, c in enumerate(countries):
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
                "climate_description": c.climate_description,
                "unique_things": c.unique_things,
                "unique_animals": c.unique_animals,
                "travel_types": json.loads(c.travel_types) if c.travel_types else {"categories": [], "highlights": []},
                "hdi": float(c.hdi) if c.hdi else None,
                "life_expectancy": float(c.life_expectancy) if c.life_expectancy else None,
                "gdp_nominal": float(c.gdp_nominal) if c.gdp_nominal else None,
                "gdp_ppp": float(c.gdp_ppp) if c.gdp_ppp else None,
                "gdp_per_capita": float(c.gdp_per_capita) if c.gdp_per_capita else None,
                "gini": float(c.gini) if c.gini else None,
                "coat_of_arms_url": c.coat_of_arms_url,
                "inception_date": c.inception_date,
                "official_tourist_website": c.official_tourist_website,
                "regional_products": c.regional_products,
                "has_ekuz": bool(c.has_ekuz),
                "latitude": float(c.latitude) if c.latitude else None,
                "longitude": float(c.longitude) if c.longitude else None,
                "unesco_count": c.unesco_count or 0,
                "is_independent": bool(c.is_independent),
                "last_updated": str(c.updated_at) if c.updated_at else None
            }
            
            # Parent & Territories
            processed_data["parent"] = {"iso2": id_to_iso.get(c.parent_id), "name_pl": id_to_name_pl.get(c.parent_id)} if c.parent_id else None
            processed_data["territories"] = [{"iso2": t.iso_alpha2, "name_pl": id_to_name_pl.get(t.id)} for t in c.territories]
            processed_data["religions"] = [{"name": r.name, "percentage": float(r.percentage)} for r in c.religions]
            processed_data["languages"] = [{"name": l.name, "is_official": l.is_official} for l in c.languages]
            
            # Safety
            if c.safety:
                processed_data["safety"] = {
                    "risk_level": c.safety.risk_level or "unknown",
                    "risk_text": c.safety.summary or "",
                    "risk_details": c.safety.risk_details or "",
                    "url": c.safety.full_url or "",
                    "last_updated": str(c.safety.last_checked) if c.safety.last_checked else None
                }
            else:
                processed_data["safety"] = {"risk_level": "unknown", "risk_text": "Brak danych.", "risk_details": "", "url": "", "last_updated": None}
            
            # Currency
            if c.currency:
                processed_data["currency"] = {
                    "code": c.currency.code,
                    "name": c.currency.name or "",
                    "rate_pln": float(c.currency.exchange_rate_pln) if c.currency.exchange_rate_pln else None,
                    "relative_cost": c.currency.relative_cost,
                    "last_updated": str(c.currency.last_updated) if c.currency.last_updated else None,
                    "denominations": [{"value": d.value, "type": d.type, "image_url": d.image_url} for d in c.currency.denominations]
                }
            else:
                processed_data["currency"] = {"code": "", "name": "", "rate_pln": None, "relative_cost": None, "last_updated": None, "denominations": []}
            
            # Practical
            if c.practical:
                processed_data["practical"] = {
                    "plug_types": c.practical.plug_types or "",
                    "voltage": c.practical.voltage,
                    "frequency": c.practical.frequency,
                    "water_safe": c.practical.tap_water_safe,
                    "water_safe_for_brushing": c.practical.water_safe_for_brushing,
                    "driving_side": c.practical.driving_side or "right",
                    "card_acceptance": c.practical.card_acceptance or "",
                    "best_exchange_currency": c.practical.best_exchange_currency or "",
                    "exchange_where": c.practical.exchange_where or "",
                    "atm_advice": c.practical.atm_advice or "",
                    "bargaining_info": c.practical.bargaining_info or "",
                    "alcohol_rules": c.practical.alcohol_rules or "",
                    "dress_code": c.practical.dress_code or "",
                    "photography_restrictions": c.practical.photography_restrictions or "",
                    "sensitive_topics": c.practical.sensitive_topics or "",
                    "local_norms": c.practical.local_norms or "",
                    "store_hours": c.practical.store_hours or "",
                    "internet_notes": c.practical.internet_notes or "",
                    "esim_available": bool(c.practical.esim_available) if c.practical.esim_available is not None else None,
                    "emergency": json.loads(c.practical.emergency_numbers) if c.practical.emergency_numbers else None,
                    "vaccinations_required": c.practical.vaccinations_required or "",
                    "vaccinations_suggested": c.practical.vaccinations_suggested or "",
                    "health_info": c.practical.health_info or "",
                    "roaming_info": c.practical.roaming_info or "",
                    "license_type": c.practical.license_type or "",
                    "souvenirs": c.practical.souvenirs or "",
                    "last_updated": str(c.practical.last_updated) if c.practical.last_updated else None
                }
            else:
                processed_data["practical"] = {"last_updated": None}

            # Lists
            processed_data["souvenirs_list"] = [{"name": s.name, "description": s.description, "category": s.category, "image_url": s.image_url} for s in c.souvenirs]
            processed_data["unesco_places"] = [{"name": u.name, "category": u.category, "is_danger": bool(u.is_danger), "unesco_id": u.unesco_id, "image_url": u.image_url} for u in c.unesco_places]
            processed_data["attractions"] = [{"name": a.name, "category": a.category, "description": a.description} for a in c.attractions[:15]]
            processed_data["holidays"] = [{"name": h.name, "date": str(h.date)} for h in c.holidays]
            processed_data["climate"] = [{"month": cl.month, "temp_day": cl.avg_temp_max, "temp_night": cl.avg_temp_min, "rain": cl.avg_rain_mm, "season": cl.season_type} for cl in c.climate]
            processed_data["laws_and_customs"] = [{"category": lc.category, "title": lc.title, "description": lc.description} for lc in c.laws_and_customs]
            
            output[c.iso_alpha2] = processed_data
            if (i+1) % 100 == 0:
                print(f"Przetworzono {i+1}/{len(countries)} krajów...")

        with open('docs/data.json', 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        print(f"Eksport zakończony sukcesem! data.json zawiera {len(output)} krajów.")
    finally:
        db.close()

if __name__ == "__main__":
    export_all()
