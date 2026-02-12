import httpx
from sqlalchemy.orm import Session
from .. import models
from datetime import datetime

async def sync_rates(db: Session):
    """Sync currency exchange rates from free API"""

    # exchangerate-api.com - 1500 requests/month free
    async with httpx.AsyncClient() as client:
        response = await client.get("https://api.exchangerate-api.com/v4/latest/PLN")
        data = response.json()

    rates = data.get('rates', {})
    updated = 0

    # Get all countries with currencies
    countries = db.query(models.Country).join(models.Currency).all()

    for country in countries:
        currency = country.currency
        if not currency:
            continue

        curr_code = currency.code

        if curr_code in rates:
            # Rate from PLN to target currency
            rate_pln = rates[curr_code]

            # Calculate inverse (target to PLN)
            currency.exchange_rate_pln = 1 / rate_pln if rate_pln > 0 else 0

            # EUR and USD
            if 'EUR' in rates:
                currency.exchange_rate_eur = rates['EUR'] / rate_pln if rate_pln > 0 else 0
            if 'USD' in rates:
                currency.exchange_rate_usd = rates['USD'] / rate_pln if rate_pln > 0 else 0

            currency.last_updated = datetime.now()
            updated += 1

    db.commit()

    return {
        "updated": updated,
        "timestamp": datetime.now().isoformat()
    }
