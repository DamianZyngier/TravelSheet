import json
import os
import sys

def test_data_integrity():
    filepath = sys.argv[1] if len(sys.argv) > 1 else 'docs/data.json'
    if not os.path.exists(filepath):
        print(f"[ERROR] {filepath} not found. Run export script first.")
        sys.exit(1)

    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    if not data:
        print("[ERROR] data.json is empty.")
        sys.exit(1)

    print(f"Validating {len(data)} countries and all fields...")
    
    errors = []
    any_unesco = False
    any_attractions = False
    any_embassies = False
    
    for iso, country in data.items():
        # 1. Basic Fields
        for field in ['name', 'name_pl', 'iso2', 'iso3', 'capital', 'continent', 'region', 'flag_url', 'unesco_count', 'wiki_summary']:
            if field not in country:
                errors.append(f"{iso}: Missing basic field '{field}'")
        
        # 2. Safety
        safety = country.get('safety', {})
        for field in ['risk_level', 'risk_text', 'risk_details', 'url']:
            if field not in safety:
                errors.append(f"{iso}: Missing safety field '{field}'")
        
        # 3. Currency
        currency = country.get('currency', {})
        for field in ['code', 'name', 'rate_pln']:
            if field not in currency:
                errors.append(f"{iso}: Missing currency field '{field}'")
        
        # 4. Practical Info
        practical = country.get('practical', {})
        fields = ['plug_types', 'voltage', 'water_safe', 'driving_side', 'card_acceptance', 
                  'emergency', 'vaccinations_required', 'vaccinations_suggested', 
                  'health_info', 'roaming_info', 'license_type']
        for field in fields:
            if field not in practical:
                errors.append(f"{iso}: Missing practical field '{field}'")
        
        # 5. Costs
        costs = country.get('costs')
        if costs:
            for field in ['index', 'restaurants', 'groceries', 'transport', 'accommodation', 'ratio_to_pl']:
                if field not in costs:
                    errors.append(f"{iso}: Missing costs field '{field}'")
        
        # 6. Entry Requirements
        entry = country.get('entry')
        if entry:
            for field in ['visa_required', 'visa_status', 'passport_required', 'temp_passport_allowed', 'id_card_allowed', 'visa_notes']:
                if field not in entry:
                    errors.append(f"{iso}: Missing entry field '{field}'")

        # 7. Weather
        weather = country.get('weather')
        if weather:
            for field in ['temp', 'condition', 'icon']:
                if field not in weather:
                    errors.append(f"{iso}: Missing weather field '{field}'")

        # 8. UNESCO Places
        unesco_places = country.get('unesco_places', [])
        if not isinstance(unesco_places, list):
            errors.append(f"{iso}: 'unesco_places' is not a list")
        if unesco_places:
            any_unesco = True
        for place in unesco_places:
            for field in ['name', 'category', 'is_danger', 'is_transnational', 'unesco_id', 'image_url', 'description']:
                if field not in place:
                    errors.append(f"{iso}: UNESCO site missing field '{field}'")

        # 9. Attractions
        attractions = country.get('attractions', [])
        if not isinstance(attractions, list):
            errors.append(f"{iso}: 'attractions' is not a list")
        if attractions:
            any_attractions = True
        for attr in attractions:
            for field in ['name', 'category', 'description']:
                if field not in attr:
                    errors.append(f"{iso}: Attraction missing field '{field}'")

        # 10. Holidays
        holidays = country.get('holidays', [])
        if not isinstance(holidays, list):
            errors.append(f"{iso}: 'holidays' is not a list")

        # 11. Climate
        climate = country.get('climate', [])
        if not isinstance(climate, list):
            errors.append(f"{iso}: 'climate' is not a list")

        # 12. Religions & Languages & Embassies
        for list_field in ['religions', 'languages', 'embassies']:
            field_val = country.get(list_field)
            if not isinstance(field_val, list):
                errors.append(f"{iso}: '{list_field}' is not a list")
            if list_field == 'embassies' and field_val:
                any_embassies = True

    # Critical check: do we have ANY data?
    # For basic seeding only, these might be empty. 
    # But for a real data.json they MUST NOT be empty.
    # We allow skipping these checks if we pass a special flag.
    is_full_check = "--full" in sys.argv
    if is_full_check:
        if not any_unesco:
            errors.append("CRITICAL: No UNESCO places found in the entire dataset!")
        if not any_attractions:
            errors.append("CRITICAL: No attractions found in the entire dataset!")
        if not any_embassies:
            errors.append("CRITICAL: No embassies found in the entire dataset!")

    if errors:
        print(f"\n[FAILED] Validation Failed! Found {len(errors)} structural issues.")
        # Group errors by type to avoid spam
        error_types = {}
        for err in errors:
            etype = err.split(': ')[1]
            error_types[etype] = error_types.get(etype, 0) + 1
        
        for etype, count in error_types.items():
            print(f"  - {etype}: {count} occurrences")
        sys.exit(1)
    else:
        print("\n[SUCCESS] All structural tests passed! All fields are present in the JSON structure.")
        sys.exit(0)

if __name__ == "__main__":
    test_data_integrity()
