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

    async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
        for country in countries:
            if country.iso_alpha2 == 'PL':
                continue
                
            try:
                iso2 = country.iso_alpha2
                name_pl = clean_polish_name(country.name_pl or country.name)
                slug = MSZ_GOV_PL_MANUAL_MAPPING.get(iso2.upper())
                
                if not slug:
                    slug = slugify(name_pl).replace('-', '')

                # Extended URL list to catch more mission types
                urls = [
                    f"https://www.gov.pl/web/{slug}/ambasada",
                    f"https://www.gov.pl/web/{slug}/placowki",
                    f"https://www.gov.pl/web/{slug}/konsulaty-honorowe",
                ]
                
                all_missions = []
                headers = get_headers()
                for url in urls:
                    try:
                        resp = await client.get(url, headers=headers)
                        if resp.status_code == 200:
                            missions = parse_embassy_page(resp.text, country.id)
                            if missions:
                                # Merge while avoiding duplicates based on address/type
                                for m in missions:
                                    if not any(existing.address == m.address and existing.type == m.type for existing in all_missions):
                                        all_missions.append(m)
                    except: continue
                
                if all_missions:
                    # Clear old ones and save new ones
                    db.query(models.Embassy).filter(models.Embassy.country_id == country.id).delete()
                    for emb in all_missions:
                        db.add(emb)
                    db.commit()
                    results["synced_countries"] += 1
                    results["total_missions"] += len(all_missions)
                
                await asyncio.sleep(0.05)
                
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
            city_match = re.search(r'w\s+([A-ZĄĆĘŁŃÓŚŹŻ][a-ząćęłńóśźż]+)', title)
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
