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
    print("📦 Eksportuję dane z SQLite do docs/data.json...")

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
        joinedload(models.Country.laws_and_customs)
    ).all()

    output = {}

    for c in countries:
        # Budujemy obiekt dla każdego kraju
        country_data = {
            "name": c.name,
            "iso2": c.iso_alpha2,
            "iso3": c.iso_alpha3,
            "capital": c.capital,
            "continent": c.continent,
            "region": c.region,
            "flag_emoji": c.flag_emoji,
            "flag_url": c.flag_url,
            "population": c.population,
            
            "safety": {
                "risk_level": c.safety.risk_level if c.safety else "unknown",
                "summary": c.safety.summary if c.safety else "",
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
                "card_acceptance": c.practical.card_acceptance if c.practical else ""
            },
            
            "weather": {
                "temp": float(c.weather.temp_c) if c.weather and c.weather.temp_c else None,
                "condition": c.weather.condition if c.weather else "",
                "icon": c.weather.condition_icon if c.weather else ""
            },
            
            "attractions": [
                {"name": a.name, "category": a.category} for a in c.attractions[:10]
            ],
            
            "holidays": [
                {"name": h.name, "date": str(h.date)} for h in c.holidays[:5]
            ]
        }
        output[c.iso_alpha2] = country_data

    # Zapisujemy do folderu docs (dla GitHub Pages)
    os.makedirs('docs', exist_ok=True)
    with open('docs/data.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    db.close()
    print(f"✅ Eksport zakończony! Plik docs/data.json zawiera {len(output)} krajów.")

if __name__ == "__main__":
    export_all()
