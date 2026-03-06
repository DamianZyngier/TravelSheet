import httpx
from sqlalchemy.orm import Session
from .. import models
from sqlalchemy.sql import func
import logging
from datetime import datetime, timedelta

logger = logging.getLogger("uvicorn")

async def sync_rates(db: Session):
    """
    Syncs currency exchange rates from NBP.
    Calculates currency strength based on comparison with historical average (approx 1 year ago).
    """
    # 1. Current rates
    urls = [
        "https://api.nbp.pl/api/exchangerates/tables/A?format=json",
        "https://api.nbp.pl/api/exchangerates/tables/B?format=json"
    ]
    
    # 2. Historical rates (for strength calculation) - approx 1 year ago
    historical_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
    hist_urls = [
        f"https://api.nbp.pl/api/exchangerates/tables/A/{historical_date}?format=json",
        f"https://api.nbp.pl/api/exchangerates/tables/B/{historical_date}?format=json"
    ]
    
    current_data = {}
    historical_data = {}
    
    async with httpx.AsyncClient(timeout=15.0) as client:
        # Fetch Current
        for url in urls:
            try:
                resp = await client.get(url)
                if resp.status_code == 200:
                    rates = resp.json()[0].get("rates", [])
                    for r in rates:
                        current_data[r["code"].upper()] = {"rate": r["mid"], "name": r["currency"]}
            except: pass
            
        # Fetch Historical (Best effort)
        for url in hist_urls:
            try:
                resp = await client.get(url)
                if resp.status_code == 200:
                    rates = resp.json()[0].get("rates", [])
                    for r in rates:
                        historical_data[r["code"].upper()] = r["mid"]
            except: pass

    if not current_data:
        return {"success": 0, "errors": 1}

    updated = 0
    currencies = db.query(models.Currency).all()
    
    for curr in currencies:
        code = curr.code.upper()
        if code in current_data:
            info = current_data[code]
            curr.exchange_rate_pln = info["rate"]
            curr.name = info["name"].capitalize()
            curr.last_updated = func.now()
            
            # Strength Logic: Is PLN stronger or weaker than a year ago?
            # If 1 CURR costs MORE PLN than before -> CURR is "Mocna" (PLN weak)
            # If 1 CURR costs LESS PLN than before -> CURR is "Słaba" (PLN strong)
            hist_rate = historical_data.get(code)
            if hist_rate:
                diff_pct = ((info["rate"] - hist_rate) / hist_rate) * 100
                if diff_pct > 5:
                    curr.relative_cost = "Waluta mocna (droga)"
                elif diff_pct < -5:
                    curr.relative_cost = "Waluta słaba (tania)"
                else:
                    curr.relative_cost = "Kurs stabilny"
            else:
                # Nominal fallback if no history
                if info["rate"] > 10: curr.relative_cost = "Wysoka wartość jedn."
                elif info["rate"] < 0.1: curr.relative_cost = "Niska wartość jedn."
                else: curr.relative_cost = "Średnia"
                
            updated += 1

    db.commit()
    return {"success": updated}
