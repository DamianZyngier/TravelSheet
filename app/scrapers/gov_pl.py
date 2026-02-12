import httpx
from bs4 import BeautifulSoup
from sqlalchemy.orm import Session
from .. import models, crud
import asyncio

# Mapowanie ISO -> slug gov.pl (trzeba uzupełnić)
COUNTRY_SLUGS = {
    'TH': 'tajlandia',
    'PL': 'polska',
    'DE': 'niemcy',
    'FR': 'francja',
    # ... etc
}

async def scrape_country(db: Session, iso_code: str):
    """Scrape MSZ data for specific country"""

    slug = COUNTRY_SLUGS.get(iso_code)
    if not slug:
        return {"error": f"No slug mapping for {iso_code}"}

    url = f"https://www.gov.pl/web/dyplomacja/informacje-dla-podrozujacych/{slug}"

    # Rate limiting - 1 request per 2 seconds
    await asyncio.sleep(2)

    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.get(url)
            response.raise_for_status()
        except:
            return {"error": f"Failed to fetch {url}"}

    soup = BeautifulSoup(response.text, 'html.parser')

    # Extract safety info (struktura HTML trzeba będzie dostosować)
    country = crud.get_country_by_iso2(db, iso_code)
    if not country:
        return {"error": "Country not found in DB"}

    # Przykład - znajdź poziom ryzyka
    risk_section = soup.find('div', class_='safety-level')  # Przykład
    if risk_section:
        risk_text = risk_section.get_text(strip=True)

        # Parse risk level
        if 'zwykłą ostrożność' in risk_text.lower():
            risk_level = 'normal_caution'
        elif 'szczególną ostrożność' in risk_text.lower():
            risk_level = 'heightened'
        else:
            risk_level = 'unknown'

        # Update or create safety info
        safety = db.query(models.SafetyInfo).filter(
            models.SafetyInfo.country_id == country.id
        ).first()

        if safety:
            safety.risk_level = risk_level
            safety.summary = risk_text[:500]
            safety.full_url = url
        else:
            safety = models.SafetyInfo(
                country_id=country.id,
                risk_level=risk_level,
                summary=risk_text[:500],
                full_url=url
            )
            db.add(safety)

        db.commit()

    return {
        "country": iso_code,
        "slug": slug,
        "scraped": True
    }
