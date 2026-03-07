import httpx
import json
import csv
import io
import re
import html
import logging
import asyncio
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy.sql import func

from .. import models
from .base import BaseScraper

logger = logging.getLogger("uvicorn")

class EmbassyScraper(BaseScraper):
    """
    Scrapes all diplomatic missions (Embassies, Consulates, etc.) from the centralized MSZ portal.
    """
    def __init__(self, db: Session, concurrency: int = 5, timeout: float = 45.0):
        super().__init__(db, concurrency, timeout)
        self.missions_by_country: Dict[int, List[models.Embassy]] = {}
        self.manual_map = {
            "usa": "stany zjednoczone",
            "stany zjednoczone ameryki": "stany zjednoczone",
            "stany zjednoczone (usa)": "stany zjednoczone",
            "zjednoczone królestwo": "wielka brytania",
            "zjednoczone królestwo wielkiej brytanii i irlandii północnej": "wielka brytania",
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

    async def run(self, countries: List[models.Country]) -> Dict[str, int]:
        """
        Overridden run to scrape all data once before distributing to sync_country calls.
        """
        url = "https://www.gov.pl/web/dyplomacja/polskie-przedstawicielstwa-na-swiecie"
        
        async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
            self.client = client
            try:
                resp = await self.client.get(url)
                content = resp.text
                
                # Data is in <pre id="registerData" class="hide">
                match = re.search(r'<pre id="registerData".*?>(.*?)</pre>', content, re.DOTALL)
                if not match:
                    logger.error("Could not find registerData for embassies scraper")
                    return {"success": 0, "errors": 1}
                
                raw_json = html.unescape(match.group(1))
                data_json = json.loads(raw_json)
                csv_data = data_json['data']
                
                # Parse CSV
                f = io.StringIO(csv_data)
                reader = csv.DictReader(f, delimiter=';')
                
                name_to_id = {c.name_pl.lower(): c.id for c in countries if c.name_pl}
                
                # Ensure mappings are in the name_to_id
                for m_key, m_val in self.manual_map.items():
                    if m_val in name_to_id:
                        name_to_id[m_key] = name_to_id[m_val]

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
                    
                    if country_id not in self.missions_by_country:
                        self.missions_by_country[country_id] = []
                    
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
                    for existing_m in self.missions_by_country[country_id]:
                        if existing_m["type"] == mission_data["type"] and (existing_m["address"] == mission_data["address"] or existing_m["email"] == mission_data["email"]):
                            is_dup = True
                            break
                    
                    if not is_dup:
                        self.missions_by_country[country_id].append(mission_data)

            except Exception as e:
                logger.error(f"Error in centralized embassy sync: {e}")
                return {"success": 0, "errors": 1}

            # Now proceed with normal _limited_sync for each country
            results = {"success": 0, "errors": 0}
            tasks = [self._limited_sync(country, results) for country in countries]
            await asyncio.gather(*tasks)
            
            return results

    async def sync_country(self, country: models.Country) -> Any:
        missions_data = self.missions_by_country.get(country.id, [])
        if not missions_data:
            return {"status": "skipped", "reason": "No embassy data found"}

        try:
            self.db.query(models.Embassy).filter(models.Embassy.country_id == country.id).delete()
            for m_data in missions_data:
                mission = models.Embassy(**m_data, last_updated=func.now())
                self.db.add(mission)
            
            self.db.commit()
            return {"status": "success", "missions_count": len(missions_data)}
        except Exception as e:
            logger.error(f"Error updating embassies for {country.iso_alpha2}: {e}")
            return {"error": str(e)}

async def scrape_embassies(db: Session):
    """
    Legacy wrapper for scraping embassies.
    """
    scraper = EmbassyScraper(db)
    countries = db.query(models.Country).all()
    results = await scraper.run(countries)
    
    # Add total_missions for backward compatibility
    total_missions = db.query(func.count(models.Embassy.id)).scalar()
    results["total_missions"] = total_missions
    
    return results
