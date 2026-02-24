import httpx
from sqlalchemy.orm import Session
from .. import models
from sqlalchemy.sql import func
import logging

logger = logging.getLogger("uvicorn")

async def sync_rates(db: Session):
    """
    Syncs currency exchange rates from NBP (National Bank of Poland).
    Covers both Table A (major currencies) and Table B (exotic currencies).
    """
    # NBP API URLs
    urls = [
        "https://api.nbp.pl/api/exchangerates/tables/A?format=json",
        "https://api.nbp.pl/api/exchangerates/tables/B?format=json"
    ]
    
    all_nbp_rates = {}
    
    async with httpx.AsyncClient(timeout=15.0) as client:
        for url in urls:
            try:
                resp = await client.get(url)
                if resp.status_code == 200:
                    data = resp.json()
                    # data is a list with one element (the table)
                    rates = data[0].get("rates", [])
                    for r in rates:
                        code = r.get("code")
                        mid = r.get("mid")
                        if code and mid:
                            all_nbp_rates[code.upper()] = mid
            except Exception as e:
                logger.error(f"Error fetching from NBP ({url}): {e}")

    if not all_nbp_rates:
        return {"error": "No rates found from NBP"}

    updated = 0
    currencies = db.query(models.Currency).all()
    
    for curr in currencies:
        # NBP returns 1 CURR = X PLN (mid rate)
        # This is exactly what we store in exchange_rate_pln
        rate = all_nbp_rates.get(curr.code.upper())
        if rate:
            curr.exchange_rate_pln = rate
            curr.last_updated = func.now()
            updated += 1

    db.commit()
    logger.info(f"Updated {updated} exchange rates from NBP")
    return {"updated": updated}
