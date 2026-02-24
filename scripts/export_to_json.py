import json
import os
import sys
from sqlalchemy.orm import joinedload

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal
from app import models

def export_all():
    db = SessionLocal()
    print("Eksportuję dane z SQLite do docs/data.json...")

    # Pobieramy wszystko z relacjami
    countries = db.query(models.Country).options(
        joinedload(models.Country.languages),
        joinedload(models.Country.religions),
        joinedload(models.Country.currency),
        joinedload(models.Country.safety),
        joinedload(models.Country.embassies),
        joinedload(models.Country.entry_req),
        joinedload(models.Country.attractions),
        joinedload(models.Country.practical),
        joinedload(models.Country.weather),
        joinedload(models.Country.climate),
        joinedload(models.Country.holidays),
        joinedload(models.Country.laws_and_customs),
        joinedload(models.Country.costs)
    ).all()

    output = {}

    for c in countries:
        # Budujemy obiekt dla każdego kraju
        country_data = {
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
            "latitude": float(c.latitude) if c.latitude else None,
            "longitude": float(c.longitude) if c.longitude else None,
            
            "safety": {
                "risk_level": c.safety.risk_level if c.safety else "unknown",
                "risk_text": c.safety.summary if c.safety else "Brak danych",
                "risk_details": c.safety.risk_details if c.safety else "",
                "url": c.safety.full_url if c.safety else ""
            },
            
            "currency": {
                "code": c.currency.code if c.currency else "",
                "name": c.currency.name if c.currency else "",
                "rate_pln": float(c.currency.exchange_rate_pln) if c.currency and c.currency.exchange_rate_pln else None
            },
            
            "practical": {
                "plug_types": c.practical.plug_types if c.practical else "",
                "voltage": c.practical.voltage if c.practical else None,
                "water_safe": c.practical.tap_water_safe if c.practical else None,
                "driving_side": c.practical.driving_side if c.practical else "",
                "card_acceptance": c.practical.card_acceptance if c.practical else "",
                "emergency": json.loads(c.practical.emergency_numbers) if c.practical and c.practical.emergency_numbers else None,
                "vaccinations_required": c.practical.vaccinations_required if c.practical else "",
                "vaccinations_suggested": c.practical.vaccinations_suggested if c.practical else "",
                "health_info": c.practical.health_info if c.practical else "",
                "roaming_info": c.practical.roaming_info if c.practical else ""
            },

            "costs": {
                "index": float(c.costs.index_overall) if c.costs else None,
                "restaurants": float(c.costs.index_restaurants) if c.costs else None,
                "groceries": float(c.costs.index_groceries) if c.costs else None,
                "transport": float(c.costs.index_transport) if c.costs else None,
                "accommodation": float(c.costs.index_accommodation) if c.costs else None,
                "ratio_to_pl": float(c.costs.ratio_to_poland) if c.costs else None
            },

            "entry": {
                "visa_required": c.entry_req.visa_required if c.entry_req else None,
                "passport_required": c.entry_req.passport_required if c.entry_req else True,
                "temp_passport_allowed": c.entry_req.temp_passport_allowed if c.entry_req else True,
                "id_card_allowed": c.entry_req.id_card_allowed if c.entry_req else False,
                "visa_notes": c.entry_req.visa_notes if c.entry_req else ""
            },
            
            "weather": {
                "temp": float(c.weather.temp_c) if c.weather and c.weather.temp_c else None,
                "condition": c.weather.condition if c.weather else "",
                "icon": c.weather.condition_icon if c.weather else ""
            },
            
            "embassies": [
                {
                    "type": e.type,
                    "city": e.city,
                    "address": e.address,
                    "phone": e.phone,
                    "email": e.email,
                    "website": e.website
                } for e in c.embassies
            ],

            "attractions": [
                {
                    "name": a.name, 
                    "category": a.category,
                    "description": a.description
                } for a in c.attractions[:15]
            ],
            
            "holidays": [
                {"name": h.name, "date": str(h.date)} 
                for h in sorted(c.holidays, key=lambda x: x.date)
            ],

            "climate": [
                {
                    "month": cl.month,
                    "temp_day": cl.avg_temp_max,
                    "temp_night": cl.avg_temp_min,
                    "rain": cl.avg_rain_mm
                } for cl in sorted(c.climate, key=lambda x: x.month)
            ]
        }
        output[c.iso_alpha2] = country_data

    # Zapisujemy do folderu docs (dla GitHub Pages)
    os.makedirs('docs', exist_ok=True)
    with open('docs/data.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    # Zapisujemy też do frontend/public (dla lokalnego developmentu)
    os.makedirs('frontend/public', exist_ok=True)
    with open('frontend/public/data.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    db.close()
    print(f"Eksport zakończony! Plik docs/data.json zawiera {len(output)} krajów.")

if __name__ == "__main__":
    export_all()
