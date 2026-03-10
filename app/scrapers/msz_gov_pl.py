import httpx
from bs4 import BeautifulSoup
from sqlalchemy.orm import Session
from typing import List, Dict
from .. import models
import asyncio
import re
import logging
from sqlalchemy import func
from .utils import MSZ_GOV_PL_MANUAL_MAPPING, clean_polish_name, slugify, get_headers, normalize_polish_text
from .base import BaseScraper

logger = logging.getLogger("uvicorn")

class MSZScraper(BaseScraper):
    def __init__(self, db: Session):
        super().__init__(db, concurrency=3, timeout=60.0)
        self.url_cache = {}

    async def fetch_directory(self):
        url = "https://www.gov.pl/web/dyplomacja/informacje-dla-podrozujacych"
        try:
            resp = await self.client.get(url, headers=get_headers())
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, 'html.parser')
            
            # The structure seems to be a list of <a> tags inside the main content
            links = soup.select('a[href*="/web/dyplomacja/"]')
            
            if not links:
                logger.warning("No MSZ directory links found with /web/dyplomacja/ selector")
            
            for a in links:
                href = a.get('href', '')
                if not href: continue
                if not href.startswith('http'): href = "https://www.gov.pl" + href
                
                # We want links like /web/dyplomacja/niemcy or /web/dyplomacja/tajlandia
                # but NOT the main page itself or generic ones
                if href.rstrip('/') == url.rstrip('/'): continue
                if any(x in href for x in ['kontakt', 'dla-mediow', 'co-robimy', 'strategia']): continue
                
                title_text = a.get_text().strip()
                if title_text and 2 <= len(title_text) <= 60:
                    self.url_cache[clean_polish_name(title_text)] = href
            
            logger.info(f"Fetched {len(self.url_cache)} country links from MSZ directory")
            # Log first few for debugging
            # logger.info(f"Sample links: {list(self.url_cache.items())[:5]}")
        except Exception as e:
            logger.error(f"Error fetching MSZ directory: {e}")

    async def sync_country(self, country: models.Country, depth: int = 0):
        if country.iso_alpha2 == 'PL': return {"status": "skipped"}

        name_pl = clean_polish_name(country.name_pl or country.name)
        dir_url = self.url_cache.get(name_pl)
        manual_slug = MSZ_GOV_PL_MANUAL_MAPPING.get(country.iso_alpha2)
        simple_slug = slugify(name_pl)

        strategies = []
        if dir_url: strategies.append(("directory", dir_url))
        if manual_slug:
            strategies.append(("manual", f"https://www.gov.pl/web/dyplomacja/{manual_slug}"))
            strategies.append(("manual-modern", f"https://www.gov.pl/web/{manual_slug}/idp"))
        strategies.append(("modern", f"https://www.gov.pl/web/{simple_slug}/idp"))

        response_text, final_url = None, ""
        for _, url in strategies:
            try:
                await asyncio.sleep(0.5)
                resp = await self.client.get(url, headers=get_headers())
                if resp.status_code == 200:
                    curr_url = str(resp.url).rstrip('/')
                    if curr_url not in ["https://www.gov.pl", "https://www.gov.pl/web/dyplomacja/informacje-dla-podrozujacych"]:
                        if any(kw in resp.text.lower() for kw in ["bezpieczeństwo", "ostrzeżenia", "idp"]):
                            response_text, final_url = resp.text, str(resp.url)
                            break
            except: continue

        if not response_text:
            if country.parent_id:
                return await self.parent_fallback(country, depth)
            return {"error": "No valid MSZ page found"}

        soup = BeautifulSoup(response_text, 'html.parser')
        risk_level = self._parse_risk_level(soup, country)
        
        # Parse all sections
        self._update_safety(country, soup, risk_level, final_url)
        self._update_entry(country, soup)
        self._update_practical(country, soup)
        self._update_customs(country, soup)
        
        self.db.commit()
        return {"status": "success"}

    def _update_customs(self, country: models.Country, soup: BeautifulSoup):
        practical = self.db.query(models.PracticalInfo).filter(models.PracticalInfo.country_id == country.id).first()
        if not practical:
            practical = models.PracticalInfo(country_id=country.id)
            self.db.add(practical)

        # Look for "Cło" section
        customs_text = ""
        
        # Strategy 1: Find by ID or header text
        headers = soup.find_all(['h2', 'h3', 'h4'])
        for h in headers:
            if 'cło' in h.get_text().lower():
                # Get next siblings until next header
                content = []
                curr = h.find_next_sibling()
                while curr and curr.name not in ['h2', 'h3', 'h4']:
                    content.append(curr.get_text().strip())
                    curr = curr.find_next_sibling()
                customs_text = "\n".join(filter(None, content))
                break
        
        # Strategy 2: Search in whole text if nothing found
        if not customs_text:
            text = soup.get_text()
            match = re.search(r'Cło(.*?)(Ubezpieczenie|Zdrowie|Religia|Wizy|Waluta|$)', text, re.S | re.I)
            if match:
                customs_text = match.group(1).strip()

        # Add EU info if applicable
        eu_members = ['AT', 'BE', 'BG', 'HR', 'CY', 'CZ', 'DK', 'EE', 'FI', 'FR', 'DE', 'GR', 'HU', 'IE', 'IT', 'LV', 'LT', 'LU', 'MT', 'NL', 'PL', 'PT', 'RO', 'SK', 'SI', 'ES', 'SE']
        eu_import_limits = "\n\n**Limity wwozowe do UE (z krajów poza UE):**\n- Wyroby tytoniowe: 200 papierosów lub 50 cygar.\n- Alkohol: 1L mocnego (>22%) lub 4L wina spokojnego i 16L piwa.\n- Inne: zakaz wwożenia mięsa i nabiału (serów) z większości krajów poza UE."
        
        if country.iso_alpha2 in eu_members:
            eu_intra_limits = "**Limity wewnątrzunijne (dla podróżnych):** 800 papierosów, 10L spirytusu, 20L wina wzmocnionego, 90L wina, 110L piwa."
            customs_text = f"{eu_intra_limits}\n\n{customs_text}".strip()
        else:
            customs_text = f"{customs_text}\n\n{eu_import_limits}".strip()

        if customs_text:
            practical.customs_rules = normalize_polish_text(customs_text)

    def _parse_risk_level(self, soup: BeautifulSoup, country: models.Country) -> tuple[str, bool]:
        risk_container = soup.select_one('.travel-advisory--risk-level') or soup.select_one('.safety-level')
        risk_level = 'low'
        is_partial = False

        if risk_container:
            text = risk_container.get_text().lower()
            if 'zachowaj zwykłą ostrożność' in text: risk_level = 'low'
            elif 'zachowaj szczególną ostrożność' in text: risk_level = 'medium'
            elif 'odradzamy podróże, które nie są konieczne' in text: risk_level = 'high'
            elif 'odradzamy wszelkie podróże' in text: risk_level = 'critical'
        
        # Text-based fallback/override
        page_text = soup.get_text().lower()
        
        # Check for partial territory warnings (often seen in Turkey, Egypt)
        # We look for the "rest of territory" phrase which defines the base level
        # This regex covers many variations including "na pozostałym terytorium Turcji/kraju/itp."
        rest_pattern = r'na pozostałym terytorium.*?(zalecamy\s+)?(zachowanie|zachować)\s+(.*?)(\.|$)'
        rest_of_territory_match = re.search(rest_pattern, page_text, re.S | re.I)
        
        if rest_of_territory_match:
            rest_text = rest_of_territory_match.group(3).lower()
            is_partial = True
            if 'zwykłej ostrożności' in rest_text: risk_level = 'low'
            elif 'szczególnej ostrożności' in rest_text: risk_level = 'medium'
            elif 'odradzamy podróże' in rest_text: risk_level = 'high'
        else:
            if re.search(r'odradza(my)? wszelkie podróże|bezwzględnie odradza(my)?', page_text, re.I):
                risk_level = 'critical'
            elif re.search(r'odradza(my)? podróże.*?które nie są konieczne', page_text, re.I | re.S):
                if risk_level in ['low', 'medium']: risk_level = 'high'
        
        return risk_level, is_partial

    def _update_safety(self, country, soup, risk_data, url):
        risk_level, is_partial = risk_data
        safety = self.db.query(models.SafetyInfo).filter(models.SafetyInfo.country_id == country.id).first()
        if not safety:
            safety = models.SafetyInfo(country_id=country.id)
            self.db.add(safety)
        
        # Simple summary extraction
        summary = ""
        # Try to find the bolded warning summary
        strong_elements = soup.find_all('strong')
        
        warnings = []
        for s in strong_elements:
            t = s.get_text().strip()
            if any(kw in t.lower() for kw in ['odradza', 'zachowaj', 'zalecamy']):
                if len(t) > 20: # Avoid short fragments
                    warnings.append(t)
        
        labels = {
            'low': 'zachowanie zwykłej ostrożności', 
            'medium': 'zachowanie szczególnej ostrożności', 
            'high': 'odradzane podróże, które nie są konieczne', 
            'critical': 'odradzane wszelkie podróże'
        }

        if is_partial:
            # If partial, we want the summary to reflect the BASE level but mention partiality
            base_advice = labels.get(risk_level, 'zachowanie ostrożności')
            summary = f"MSZ zaleca {base_advice} na większości terytorium (ostrzeżenia punktowe)."
        else:
            # If NOT partial, we should prioritize the label-based summary to avoid
            # picking up a specific warning (like 'be careful when swimming') as the main level
            summary = f"Ministerstwo Spraw Zagranicznych zaleca {labels.get(risk_level, 'zachowanie ostrożności')}."
            
            # Optional: if there's a strong warning in the text, we can still try to find it
            # but ONLY if it matches the risk_level we found.
            if warnings:
                for w in warnings:
                    w_lower = w.lower()
                    if risk_level == 'critical' and 'odradza wszelkie' in w_lower: summary = w; break
                    if risk_level == 'high' and 'odradza podróże' in w_lower: summary = w; break
                    if risk_level == 'medium' and 'szczególną ostrożność' in w_lower: summary = w; break
                    if risk_level == 'low' and 'zwykłą ostrożność' in w_lower: summary = w; break

        safety.risk_level = risk_level
        safety.is_partial = is_partial
        safety.summary = normalize_polish_text(summary)
        safety.full_url = url
        safety.last_checked = func.now()

    def _update_entry(self, country, soup):
        entry = self.db.query(models.EntryRequirement).filter(models.EntryRequirement.country_id == country.id).first()
        if not entry:
            entry = models.EntryRequirement(country_id=country.id)
            self.db.add(entry)
        
        # Default logic for Europe
        if country.continent == 'Europe' and country.iso_alpha2 not in ['BY', 'RU', 'UA', 'GB']:
            entry.id_card_allowed = True
            entry.visa_required = False
        
        entry.last_updated = func.now()

    def _update_practical(self, country, soup):
        practical = self.db.query(models.PracticalInfo).filter(models.PracticalInfo.country_id == country.id).first()
        if not practical:
            practical = models.PracticalInfo(country_id=country.id)
            self.db.add(practical)
        practical.last_updated = func.now()

    async def run(self, countries: List[models.Country]) -> Dict[str, int]:
        async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
            self.client = client
            await self.fetch_directory()
            tasks = [self._limited_sync(country, {"success": 0, "errors": 0}) for country in countries]
            # Custom run because we need to return results
            results = {"success": 0, "errors": 0}
            for task in asyncio.as_completed(tasks):
                await task # _limited_sync updates shared results dict if passed, but here it's easier to just track
            # Redoing run to match BaseScraper but with directory fetch
            return await super().run(countries)

async def scrape_all_with_cache(db: Session):
    countries = db.query(models.Country).all()
    scraper = MSZScraper(db)
    # We call run which handles client and directory
    return await scraper.run(countries)
