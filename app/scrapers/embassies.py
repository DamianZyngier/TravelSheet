import httpx
import json
import csv
import io
import re
import html
import logging
from sqlalchemy.orm import Session
from .. import models
from sqlalchemy.sql import func

logger = logging.getLogger("uvicorn")

async def scrape_embassies(db: Session):
    """
    Scrapes all diplomatic missions (Embassies, Consulates, etc.) from the centralized MSZ portal.
    """
    url = "https://www.gov.pl/web/dyplomacja/polskie-przedstawicielstwa-na-swiecie"
    results = {"success": 0, "total_missions": 0, "errors": 0}

    try:
        async with httpx.AsyncClient(timeout=45.0) as client:
            resp = await client.get(url)
            content = resp.text
            
            # Data is in <pre id="registerData" class="hide">
            match = re.search(r'<pre id="registerData".*?>(.*?)</pre>', content, re.DOTALL)
            if not match:
                logger.error("Could not find registerData for embassies scraper")
                results["errors"] += 1
                return results
            
            raw_json = html.unescape(match.group(1))
            data_json = json.loads(raw_json)
            csv_data = data_json['data']
            
            # Parse CSV
            f = io.StringIO(csv_data)
            reader = csv.DictReader(f, delimiter=';')
            
            # Load countries for mapping
            countries = db.query(models.Country).all()
            name_to_id = {c.name_pl.lower(): c.id for c in countries if c.name_pl}
            
            # Add manual mapping overrides
            manual_map = {
                "usa": "stany zjednoczone",
                "stany zjednoczone ameryki": "stany zjednoczone",
                "stany zjednoczone (usa)": "stany zjednoczone",
                "wielka brytania": "zjednoczone królestwo",
                "zjednoczone królestwo wielkiej brytanii i irlandii północnej": "zjednoczone królestwo",
                "zjednoczone emiraty arabskie": "emiraty arabskie",
                "emiraty": "emiraty arabskie",
                "republika korei": "korea południowa",
                "korea południowa (republika korei)": "korea południowa",
                "korea północna (krld)": "korea północna",
                "chińska republika ludowa": "chiny",
                "brunei darussalam": "brunei",
                "holandia (królestwo niderlandów)": "holandia",
                "holandia (niderlandy)": "holandia",
                "niderlandy": "holandia",
                "republika południowej afryki": "południowa afryka",
                "rpa": "południowa afryka",
                "szwajcaria (konfederacja helwecka)": "szwajcaria"
            }
            
            # Ensure mappings are in the name_to_id
            for m_key, m_val in manual_map.items():
                if m_val in name_to_id:
                    name_to_id[m_key] = name_to_id[m_val]

            missions_by_country = {}
            
            for row in reader:
                p_name = row['Państwo / Terytorium'].strip().lower()
                country_id = name_to_id.get(p_name)
                
                # Try partial match if no exact match
                if not country_id:
                    for db_name, db_id in name_to_id.items():
                        if db_name in p_name or p_name in db_name:
                            country_id = db_id
                            break
                
                if not country_id:
                    continue
                
                if country_id not in missions_by_country:
                    missions_by_country[country_id] = []
                
                # Extract city and type
                m_type = "Placówka"
                placowka_text = row['Placówka'].lower()
                if "ambasada" in placowka_text: m_type = "Ambasada"
                elif "konsulat honorowy" in placowka_text: m_type = "Konsulat Honorowy"
                elif "konsulat generalny" in placowka_text: m_type = "Konsulat Generalny"
                elif "wydział konsularny" in placowka_text: m_type = "Wydział Konsularny"
                elif "konsulat" in placowka_text: m_type = "Konsulat"
                elif "brak polskiej placówki" in placowka_text: continue
                
                # Combine address and postal code
                addr = row['Adres'].strip()
                postal = row['Kod pocztowy'].strip()
                full_address = f"{postal} {addr}".strip() if postal else addr
                
                mission_data = {
                    "country_id": country_id,
                    "type": m_type,
                    "city": row['Miasto'].strip(),
                    "address": full_address,
                    "phone": row['Telefon'].strip(),
                    "emergency_phone": row['Telefon dyżurny'].strip(),
                    "email": row['Adres e-mail'].strip(),
                    "website": row['Strona internetowa'].strip()
                }
                
                # Simple deduplication
                is_dup = False
                for existing_m in missions_by_country[country_id]:
                    if existing_m.type == mission_data["type"] and (existing_m.address == mission_data["address"] or existing_m.email == mission_data["email"]):
                        is_dup = True
                        break
                
                if not is_dup:
                    mission = models.Embassy(**mission_data, last_updated=func.now())
                    missions_by_country[country_id].append(mission)

            # Update database
            synced_count = 0
            total_missions = 0
            for country_id, missions in missions_by_country.items():
                try:
                    db.query(models.Embassy).filter(models.Embassy.country_id == country_id).delete()
                    for m in missions:
                        db.add(m)
                    synced_count += 1
                    total_missions += len(missions)
                except Exception as e:
                    logger.error(f"Error updating embassies for country {country_id}: {e}")
                    results["errors"] += 1
            
            db.commit()
            results["success"] = synced_count
            results["total_missions"] = total_missions
            logger.info(f"Centralized embassy sync complete: {synced_count} countries, {total_missions} missions")
            
    except Exception as e:
        logger.error(f"Error in centralized embassy sync: {e}")
        results["errors"] += 1

    return results
