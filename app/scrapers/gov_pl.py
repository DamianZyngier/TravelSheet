import httpx
from bs4 import BeautifulSoup
from sqlalchemy.orm import Session
from .. import models, crud
import asyncio

# Mapowanie ISO -> slug gov.pl
COUNTRY_SLUGS = {
    'TH': 'tajlandia',
    'PL': 'polska',
    'DE': 'niemcy',
    'FR': 'francja',
    'EG': 'egipt',
    'IT': 'wlochy',
    'GR': 'grecja',
    'ES': 'hiszpania',
    'TR': 'turcja',
    'HR': 'chorwacja',
    'US': 'stany-zjednoczone-ameryki',
    'GB': 'wielka-brytania',
    'JP': 'japonia',
    'AE': 'zjednoczone-emiraty-arabskie',
    'CY': 'cypr',
    'PT': 'portugalia',
    'MA': 'maroko',
    'TN': 'tunezja',
    'BR': 'brazylia',
    'CZ': 'republika-czeska',
    'AT': 'austria',
}

async def scrape_country(db: Session, iso_code: str):
    """Scrape MSZ data for specific country"""

    slug = COUNTRY_SLUGS.get(iso_code.upper())
    if not slug:
        return {"error": f"No slug mapping for {iso_code}"}

    url = f"https://www.gov.pl/web/dyplomacja/informacje-dla-podrozujacych/{slug}"

    async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
        try:
            response = await client.get(url)
            response.raise_for_status()
        except Exception as e:
            return {"error": f"Failed to fetch {url}: {str(e)}"}

    soup = BeautifulSoup(response.text, 'html.parser')

    country = crud.get_country_by_iso2(db, iso_code)
    if not country:
        return {"error": "Country not found in DB"}

    # Extract Risk Level from MSZ specific classes
    risk_level = "unknown"
    risk_container = soup.select_one('.travel-advisory--risk-level') or soup.select_one('.safety-level')
    
    if risk_container:
        text = risk_container.get_text().lower()
        if 'zachowaj zwykłą ostrożność' in text:
            risk_level = 'low'
        elif 'zachowaj szczególną ostrożność' in text:
            risk_level = 'medium'
        elif 'odradzamy podróże, które nie są konieczne' in text:
            risk_level = 'high'
        elif 'odradzamy wszelkie podróże' in text:
            risk_level = 'critical'

    # Extract Safety Summary
    summary = ""
    safety_header = soup.find('h3', string=lambda x: x and 'Bezpieczeństwo' in x)
    if safety_header:
        # Get next few paragraphs
        paragraphs = []
        curr = safety_header.find_next_sibling()
        count = 0
        while curr and curr.name == 'p' and count < 3:
            paragraphs.append(curr.get_text(strip=True))
            curr = curr.find_next_sibling()
            count += 1
        summary = "\n".join(paragraphs)

    # Update or create safety info
    safety = db.query(models.SafetyInfo).filter(models.SafetyInfo.country_id == country.id).first()
    if safety:
        safety.risk_level = risk_level
        safety.summary = summary[:1000]
        safety.full_url = url
    else:
        safety = models.SafetyInfo(country_id=country.id, risk_level=risk_level, summary=summary[:1000], full_url=url)
        db.add(safety)

    db.commit()
    return {"status": "success", "risk_level": risk_level, "summary_len": len(summary)}

    return {
        "country": iso_code,
        "slug": slug,
        "scraped": True
    }
