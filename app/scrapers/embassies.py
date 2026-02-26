import httpx
from bs4 import BeautifulSoup
from sqlalchemy.orm import Session
from .. import models
import asyncio
import re
import logging
from .utils import MSZ_GOV_PL_MANUAL_MAPPING, clean_polish_name, get_headers, slugify

logger = logging.getLogger("uvicorn")

async def scrape_embassies(db: Session):
    """
    Scrapes all diplomatic missions (Embassies, Consulates, etc.) for all countries.
    """
    countries = db.query(models.Country).all()
    results = {"synced_countries": 0, "total_missions": 0, "errors": 0}

    async with httpx.AsyncClient(timeout=30.0, follow_redirects=False) as client:
        for country in countries:
            if country.iso_alpha2 == 'PL':
                continue
                
            try:
                iso2 = country.iso_alpha2
                name_pl = clean_polish_name(country.name_pl or country.name)
                slug = MSZ_GOV_PL_MANUAL_MAPPING.get(iso2.upper())
                
                if not slug:
                    slug = slugify(name_pl).replace('-', '')

                headers = get_headers()
                if "Accept" in headers: del headers["Accept"]
                headers["Accept"] = "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8"

                discovered_urls = set()
                
                async def discover_from_url(target_url, depth=0):
                    if depth > 1: return
                    try:
                        resp = await client.get(target_url, headers=headers)
                        if resp.status_code == 200:
                            soup = BeautifulSoup(resp.text, 'html.parser')
                            # 1. Discover from menu
                            menu = soup.select_one('#unit-menu-list') or soup.select_one('.unit-menu')
                            # 2. Discover from main content (especially for 'placowki' list)
                            content = soup.select_one('.editor-content') or soup.select_one('.art-prev') or soup.select_one('article')
                            
                            elements_to_search = []
                            if menu: elements_to_search.append(menu)
                            if content: elements_to_search.append(content)
                            
                            for root in elements_to_search:
                                for a in root.select('a'):
                                    href = a.get('href', '')
                                    text = a.get_text().lower()
                                    if any(kw in text or kw in href.lower() for kw in ["ambasada", "konsulat", "placowki", "placówki", "wydzial", "wydział"]):
                                        full_url = ""
                                        if href.startswith('/'): full_url = f"https://www.gov.pl{href}"
                                        elif href.startswith('http') and f"/web/{slug}" in href: full_url = href
                                        
                                        if full_url and full_url not in discovered_urls:
                                            # Avoid adding the directory itself to the final scrape list if we are going to recurse
                                            if "placowki" in full_url.lower() and depth == 0:
                                                await discover_from_url(full_url, depth + 1)
                                            discovered_urls.add(full_url)
                    except Exception as e:
                        logger.debug(f"Discovery failed for {target_url}: {e}")

                # 1. Start discovery from homepage
                await discover_from_url(f"https://www.gov.pl/web/{slug}")

                # 2. Add fallback/guessed URLs
                fallback_patterns = [
                    "ambasada", "ambasada-rp", "placowki", "konsulaty-honorowe", "wydzial-konsularny"
                ]
                for p in fallback_patterns:
                    discovered_urls.add(f"https://www.gov.pl/web/{slug}/{p}")

                all_missions = []
                for url in discovered_urls:
                    try:
                        resp = await client.get(url, headers=headers)
                        # Handle redirects manually
                        if resp.status_code in [301, 302]:
                            loc = resp.headers.get("location", "")
                            if loc == "/" or loc == "https://www.gov.pl/": continue
                            target = loc if loc.startswith("http") else f"https://www.gov.pl{loc}"
                            resp = await client.get(target, headers=headers)

                        if resp.status_code == 200:
                            # Verify it's not the homepage
                            if "Portal Gov.pl" in resp.text and "Polska w" not in resp.text and slug not in resp.text.lower():
                                continue
                                
                            missions = parse_embassy_page(resp.text, country.id)
                            if missions:
                                for m in missions:
                                    # Deduplicate
                                    if not any(existing.type == m.type and (existing.address == m.address or existing.email == m.email) for existing in all_missions):
                                        all_missions.append(m)
                    except: continue

                if all_missions:
                    db.query(models.Embassy).filter(models.Embassy.country_id == country.id).delete()
                    for emb in all_missions:
                        db.add(emb)
                    db.commit()
                    results["synced_countries"] += 1
                    results["total_missions"] += len(all_missions)
                    logger.info(f"Synced {len(all_missions)} missions for {country.iso_alpha2}")
                else:
                    logger.warning(f"No missions found for {country.iso_alpha2}")
                
                await asyncio.sleep(0.1)
                
            except Exception as e:
                logger.error(f"Error scraping missions for {country.iso_alpha2}: {e}")
                results["errors"] += 1

    return results

def parse_embassy_page(html, country_id):
    soup = BeautifulSoup(html, 'html.parser')
    missions = []
    
    content = soup.select_one('.editor-content') or soup.select_one('article')
    if not content:
        return None

    # Strategy: Split by headers (h2, h3, strong) to find individual missions
    
    sections = []
    current_section = {"title": "Ambasada", "content": ""}
    
    for element in content.descendants:
        if element.name in ['h2', 'h3']:
            header_text = element.get_text().strip()
            # Stop if we hit data protection sections
            if any(term in header_text.lower() for term in ["ochrona danych", "rodo", "przetwarzanie danych"]):
                break
            if current_section["content"].strip():
                sections.append(current_section)
            current_section = {"title": header_text, "content": ""}
        elif element.name is None: # text node
            current_section["content"] += element
            
    if current_section["content"].strip():
        # Final check for data protection terms in content if no more headers
        if not any(term in current_section["content"].lower() for term in ["prezes urzędu ochrony danych", "stawki 2"]):
            sections.append(current_section)

    # If no headers found, treat whole content as one section
    if not sections:
        text = content.get_text()
        # Clean text from GDPR stuff if no headers present
        gdpr_start = re.search(r'(Ochrona danych osobowych|RODO|Informacja o przetwarzaniu)', text, re.I)
        if gdpr_start:
            text = text[:gdpr_start.start()]
        sections = [{"title": "Placówka", "content": text}]

    for section in sections:
        title = section["title"]
        text = section["content"]
        
        # Regex extraction
        address_match = re.search(r'Adres:\s*(.*?)(?=\n|Telefon|E-mail|Fax|Strona|$)', text, re.I | re.S)
        phone_match = re.search(r'Telefon:\s*(.*?)(?=\n|E-mail|Fax|Strona|$)', text, re.I | re.S)
        email_match = re.search(r'E-mail:\s*([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', text, re.I)
        web_match = re.search(r'Strona internetowa:\s*(https?://[^\s\n]+)', text, re.I)
        
        # Only add if we have at least an address or contact info
        if address_match or phone_match or email_match:
            addr = address_match.group(1).strip() if address_match else None
            
            # CRITICAL: Skip if address is PUODO/Warsaw for a foreign country
            if addr and "00-193 Warszawa" in addr:
                continue
            if addr and "Stawki 2" in addr:
                continue
            
            # Detect type from title
            m_type = "Ambasada"
            if "konsulat honorowy" in title.lower(): m_type = "Konsulat Honorowy"
            elif "konsulat generalny" in title.lower(): m_type = "Konsulat Generalny"
            elif "wydział konsularny" in title.lower(): m_type = "Wydział Konsularny"
            elif "konsulat" in title.lower(): m_type = "Konsulat"
            
            # Extract city from title or address
            city = ""
            # Support accented characters in city names (e.g. Brasílii)
            city_match = re.search(r'w\s+([A-ZĄĆĘŁŃÓŚŹŻ][a-ząćęłńóśźżA-Za-z\u00C0-\u017F]+)', title)
            if city_match: city = city_match.group(1)
            
            mission = models.Embassy(
                country_id=country_id,
                type=m_type,
                city=city,
                address=address_match.group(1).strip() if address_match else None,
                phone=phone_match.group(1).strip() if phone_match else None,
                email=email_match.group(1).strip() if email_match else None,
                website=web_match.group(1).strip() if web_match else None
            )
            missions.append(mission)
            
    return missions
