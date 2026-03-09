import logging
from bs4 import BeautifulSoup
from sqlalchemy.orm import Session
from .. import models
from .utils import CDC_MAPPING, slugify, get_headers
from .base import BaseScraper

logger = logging.getLogger("uvicorn")

class CDCHealthScraper(BaseScraper):
    def __init__(self, db: Session):
        super().__init__(db, concurrency=10, timeout=60.0)

    def get_cdc_slug(self, country: models.Country) -> str:
        if country.iso_alpha2 in CDC_MAPPING:
            return CDC_MAPPING[country.iso_alpha2]
        # Handle common name variations
        name = country.name.lower()
        if "republic of the" in name: name = name.replace("republic of the ", "")
        if "kingdom of" in name: name = name.replace("kingdom of ", "")
        return slugify(name)

    async def sync_country(self, country: models.Country, depth: int = 0):
        slug = self.get_cdc_slug(country)
        urls = [
            f"https://wwwnc.cdc.gov/travel/destinations/traveler/none/{slug}",
            f"https://wwwnc.cdc.gov/travel/destinations/traveler/none/{slug}-sar",
            f"https://wwwnc.cdc.gov/travel/destinations/traveler/none/{slug}-islands"
        ]
        
        for url in urls:
            try:
                resp = await self.client.get(url, headers=get_headers(accept="text/html"))
                if resp.status_code == 200:
                    soup = BeautifulSoup(resp.text, 'html.parser')
                    vax_table = soup.select_one('table#dest-vm-a') or \
                                soup.select_one('table.disease') or \
                                soup.select_one('table.vax-list-table')
                    
                    required, suggested = [], []
                    
                    if not vax_table:
                        if country.iso_alpha2 in ['US', 'AQ', 'PL']:
                            suggested = ["Zalecane szczepienia rutynowe"]
                        else:
                            continue
                    else:
                        rows = vax_table.select('tbody tr')
                        for row in rows:
                            cells = row.find_all('td')
                            if len(cells) >= 2:
                                name = cells[0].get_text(strip=True)
                                rec = cells[1].get_text(" ", strip=True) 
                                if any(word in rec.lower() for word in ["required", "mandatory"]):
                                    required.append(name)
                                else:
                                    suggested.append(name)

                    practical = await self.get_or_create(models.PracticalInfo, country.id)
                    practical.vaccinations_required = ", ".join(required) if required else ""
                    practical.vaccinations_suggested = ", ".join(suggested) if suggested else ""
                    self.db.commit()
                    return {"status": "success"}
                elif resp.status_code == 404:
                    continue
                else:
                    return {"error": f"CDC returned {resp.status_code}"}
            except Exception as e:
                return {"error": f"{type(e).__name__}: {str(e)}"}

        # Final Fallback to Parent
        return await self.parent_fallback(country, depth)

async def sync_all_cdc(db: Session):
    countries = db.query(models.Country).all()
    scraper = CDCHealthScraper(db)
    return await scraper.run(countries)
