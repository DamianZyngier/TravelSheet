import httpx
from sqlalchemy.orm import Session
from .. import models
from sqlalchemy.sql import func
import logging

logger = logging.getLogger("uvicorn")

async def sync_rates(db: Session):
    """
    Syncs currency exchange rates and official Polish names from NBP (National Bank of Poland).
    Covers both Table A (major currencies) and Table B (exotic currencies).
    """
    # NBP API URLs
    urls = [
        "https://api.nbp.pl/api/exchangerates/tables/A?format=json",
        "https://api.nbp.pl/api/exchangerates/tables/B?format=json"
    ]
    
    all_nbp_data = {} # code -> {rate, name}
    
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
                        name = r.get("currency")
                        if code and mid:
                            all_nbp_data[code.upper()] = {
                                "rate": mid,
                                "name": name
                            }
            except Exception as e:
                logger.error(f"Error fetching from NBP ({url}): {e}")

    if not all_nbp_data:
        return {"error": "No rates found from NBP"}

    updated = 0
    names_updated = 0
    currencies = db.query(models.Currency).all()
    
    for curr in currencies:
        # NBP returns 1 CURR = X PLN (mid rate)
        nbp_info = all_nbp_data.get(curr.code.upper())
        if nbp_info:
            # Update rate
            curr.exchange_rate_pln = nbp_info["rate"]
            curr.last_updated = func.now()
            
            # Update name to official Polish if available
            if nbp_info["name"]:
                # NBP sometimes uses lowercase, capitalize first letter
                name = nbp_info["name"]
                if name:
                    name = name[0].upper() + name[1:]
                curr.name = name
                names_updated += 1
                
            updated += 1

    db.commit()
    logger.info(f"Updated {updated} exchange rates and {names_updated} names from NBP")
    return {"updated": updated, "names_updated": names_updated}
