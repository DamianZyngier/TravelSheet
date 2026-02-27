import sqlite3
import json
import os

db_path = 'travel_cheatsheet.db'

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

def export_all():
    print("Eksportuję dane (Direct SQLite Mode - ultra safe)...")
    conn = sqlite3.connect(db_path)
    conn.row_factory = dict_factory
    cur = conn.cursor()
    
    try:
        # 1. Pobierz kraje
        cur.execute("SELECT * FROM countries")
        countries = cur.fetchall()
        print(f"Pobrano {len(countries)} krajów.")
        
        output = {}
        for i, c in enumerate(countries):
            c_id = c['id']
            iso2 = c['iso_alpha2']
            
            # Pobierz relacje dla tego kraju
            # Safety
            cur.execute(f"SELECT * FROM safety_info WHERE country_id={c_id}")
            safety = cur.fetchone()
            
            # Practical
            cur.execute(f"SELECT * FROM practical_info WHERE country_id={c_id}")
            practical = cur.fetchone()
            
            # Currency
            cur.execute(f"SELECT * FROM currencies WHERE country_id={c_id}")
            currency = cur.fetchone()
            
            # Weather
            cur.execute(f"SELECT * FROM weather WHERE country_id={c_id}")
            weather = cur.fetchone()
            
            # Costs
            cur.execute(f"SELECT * FROM cost_of_living WHERE country_id={c_id}")
            costs = cur.fetchone()
            
            # Entry
            cur.execute(f"SELECT * FROM entry_requirements WHERE country_id={c_id}")
            entry = cur.fetchone()
            
            # Lists
            cur.execute(f"SELECT * FROM languages WHERE country_id={c_id}")
            languages = cur.fetchall()
            
            cur.execute(f"SELECT * FROM religions WHERE country_id={c_id}")
            religions = cur.fetchall()
            
            cur.execute(f"SELECT * FROM embassies WHERE country_id={c_id}")
            embassies = cur.fetchall()
            
            cur.execute(f"SELECT * FROM unesco_places WHERE country_id={c_id}")
            unesco = cur.fetchall()
            
            cur.execute(f"SELECT * FROM attractions WHERE country_id={c_id} LIMIT 15")
            attractions = cur.fetchall()
            
            cur.execute(f"SELECT * FROM holidays WHERE country_id={c_id} ORDER BY date")
            holidays = cur.fetchall()
            
            cur.execute(f"SELECT * FROM climate WHERE country_id={c_id} ORDER BY month")
            climate = cur.fetchall()
            
            # Budowa obiektu
            country_data = {
                "name": c['name'],
                "name_pl": c['name_pl'] or c['name'],
                "iso2": iso2,
                "iso3": c['iso_alpha3'],
                "capital": c['capital_pl'] or c['capital'],
                "continent": c['continent'],
                "region": c['region'],
                "flag_emoji": c['flag_emoji'],
                "flag_url": c['flag_url'],
                "population": c['population'],
                "area": float(c['area']) if c['area'] else None,
                "timezone": c['timezone'],
                "national_dish": c['national_dish'],
                "wiki_summary": c['wiki_summary'],
                "national_symbols": c['national_symbols'],
                "phone_code": c['phone_code'],
                "largest_cities": c['largest_cities'],
                "ethnic_groups": c['ethnic_groups'],
                "latitude": float(c['latitude']) if c['latitude'] else None,
                "longitude": float(c['longitude']) if c['longitude'] else None,
                "unesco_count": c['unesco_count'] or 0,
                
                "religions": [{"name": r['name'], "percentage": float(r['percentage'])} for r in religions],
                "languages": [{"name": l['name'], "is_official": l['is_official']} for l in languages],
                
                "safety": {
                    "risk_level": safety['risk_level'] if safety else "unknown",
                    "risk_text": safety['summary'] if safety else "Brak danych",
                    "risk_details": safety['risk_details'] if safety else "",
                    "url": safety['full_url'] if safety else ""
                },
                
                "currency": {
                    "code": currency['code'] if currency else "",
                    "name": currency['name'] if currency else "",
                    "rate_pln": float(currency['exchange_rate_pln']) if currency and currency['exchange_rate_pln'] else None
                },
                
                "practical": {
                    "plug_types": practical['plug_types'] if practical else "",
                    "voltage": practical['voltage'] if practical else None,
                    "water_safe": practical['tap_water_safe'] if practical else None,
                    "driving_side": practical['driving_side'] if practical else "",
                    "card_acceptance": practical['card_acceptance'] if practical else "",
                    "emergency": json.loads(practical['emergency_numbers']) if practical and practical['emergency_numbers'] else None,
                    "vaccinations_required": practical['vaccinations_required'] if practical else "",
                    "vaccinations_suggested": practical['vaccinations_suggested'] if practical else "",
                    "health_info": practical['health_info'] if practical else "",
                    "roaming_info": practical['roaming_info'] if practical else "",
                    "license_type": practical['license_type'] if practical else ""
                },

                "costs": {
                    "index": float(costs['index_overall']) if costs else None,
                    "restaurants": float(costs['index_restaurants']) if costs else None,
                    "groceries": float(costs['index_groceries']) if costs else None,
                    "transport": float(costs['index_transport']) if costs else None,
                    "accommodation": float(costs['index_accommodation']) if costs else None,
                    "ratio_to_pl": float(costs['ratio_to_poland']) if costs else None
                },

                "entry": {
                    "visa_required": entry['visa_required'] if entry else None,
                    "visa_status": entry['visa_status'] if entry else "",
                    "passport_required": entry['passport_required'] if entry else True,
                    "temp_passport_allowed": entry['temp_passport_allowed'] if entry else True,
                    "id_card_allowed": entry['id_card_allowed'] if entry else False,
                    "visa_notes": entry['visa_notes'] if entry else ""
                },
                
                "weather": {
                    "temp": float(weather['temp_c']) if weather and weather['temp_c'] else None,
                    "condition": weather['condition'] if weather else "",
                    "icon": weather['condition_icon'] if weather else ""
                },
                
                "embassies": [
                    {
                        "type": e['type'],
                        "city": e['city'],
                        "address": e['address'],
                        "phone": e['phone'],
                        "email": e['email'],
                        "website": e['website']
                    } for e in embassies
                ],

                "unesco_places": [
                    {
                        "name": u['name'],
                        "category": u['category'],
                        "is_danger": bool(u['is_danger']),
                        "is_transnational": bool(u['is_transnational']),
                        "unesco_id": u['unesco_id'],
                        "image_url": u['image_url'],
                        "description": u['description']
                    } for u in unesco
                ],

                "attractions": [
                    {
                        "name": a['name'], 
                        "category": a['category'],
                        "description": a['description']
                    } for a in attractions
                ],
                
                "holidays": [{"name": h['name'], "date": str(h['date'])} for h in holidays],
                "climate": [
                    {
                        "month": cl['month'],
                        "temp_day": cl['avg_temp_max'],
                        "temp_night": cl['avg_temp_min'],
                        "rain": cl['avg_rain_mm']
                    } for cl in climate
                ]
            }
            output[iso2] = country_data
            if (i+1) % 25 == 0:
                print(f"Przetworzono {i+1}/{len(countries)} krajów...")

        # Save to files
        os.makedirs('docs', exist_ok=True)
        with open('docs/data.json', 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)

        os.makedirs('frontend/public', exist_ok=True)
        with open('frontend/public/data.json', 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)

        print(f"Eksport zakończony sukcesem! data.json zawiera {len(output)} krajów.")

    finally:
        conn.close()

if __name__ == "__main__":
    export_all()
