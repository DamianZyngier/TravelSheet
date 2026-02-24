import httpx
from sqlalchemy.orm import Session
from .. import models
from sqlalchemy.sql import func
import logging

logger = logging.getLogger("uvicorn")

async def sync_rates(db: Session):
    """
    Syncs currency exchange rates from NBP (National Bank of Poland) or exchangerate.host
    """
    # Using exchangerate.host (free for basic usage)
    url = "https://api.exchangerate.host/latest?base=PLN"
    
    async with httpx.AsyncClient(timeout=15.0) as client:
        try:
            resp = await client.get(url)
            if resp.status_code != 200:
                # Fallback to a different API if needed
                return {"error": "Exchange rate API failed"}
            
            data = resp.json()
            rates = data.get("rates", {})
        except Exception as e:
            return {"error": str(e)}

    if not rates:
        return {"error": "No rates found"}

    updated = 0
    currencies = db.query(models.Currency).all()
    
    for curr in currencies:
        # exchangerate.host returns rates vs base (PLN)
        # We want 1 CURR = X PLN, so we need 1/rate
        rate_vs_pln = rates.get(curr.code)
        if rate_vs_pln and rate_vs_pln != 0:
            actual_rate = 1.0 / rate_vs_pln
            curr.exchange_rate_pln = actual_rate
            curr.last_updated = func.now()
            updated += 1

    db.commit()
    logger.info(f"Updated {updated} exchange rates")
    return {"updated": updated}
