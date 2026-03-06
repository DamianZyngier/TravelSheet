import httpx
import asyncio
from sqlalchemy.orm import Session
from .. import models
from .utils import async_sparql_get
import logging

logger = logging.getLogger("uvicorn")

async def sync_currency_visuals(db: Session, country_batch: list[models.Country]):
    """Fetch banknotes and coins images from Wikidata for a batch of countries"""
    if not country_batch: return
    
    curr_map = {}
    for c in country_batch:
        if c.currency and c.currency.code:
            curr_map[c.currency.code.upper()] = c.currency
            
    if not curr_map: return
    codes = ' '.join([f'"{code}"' for code in curr_map.keys()])
    
    # Improved query using multiple relationship paths
    query = f"""
    SELECT DISTINCT ?currCode ?denomValue ?typeLabel ?image WHERE {{
      VALUES ?currCode {{ {codes} }}
      ?curr wdt:P498 ?currCode.
      {{
        ?denom wdt:P31 ?type;
               wdt:P361 ?curr;
               wdt:P18 ?image.
      }} UNION {{
        ?denom wdt:P31 ?type;
               wdt:P1542 ?curr;
               wdt:P18 ?image.
      }} UNION {{
        ?curr wdt:P1542 ?denom.
        ?denom wdt:P31 ?type;
               wdt:P18 ?image.
      }}
      VALUES ?type {{ wd:Q47433 wd:Q41207 wd:Q11040348 }} 
      OPTIONAL {{ ?denom wdt:P1071 ?denomValue. }}
      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "pl,en". }}
    }}
    LIMIT 100
    """
    
    results = await async_sparql_get(query, "Currency Visuals")
    
    # Manual high-quality fallbacks for popular currencies
    FALLBACKS = {
        'PLN': [
            {'v': '10 Zł', 't': 'banknote', 'u': 'https://upload.wikimedia.org/wikipedia/commons/4/4b/10_zl_obverse.jpg'},
            {'v': '20 Zł', 't': 'banknote', 'u': 'https://upload.wikimedia.org/wikipedia/commons/5/5a/20_zl_obverse.jpg'},
            {'v': '50 Zł', 't': 'banknote', 'u': 'https://upload.wikimedia.org/wikipedia/commons/a/a7/50_zl_obverse.jpg'},
            {'v': '100 Zł', 't': 'banknote', 'u': 'https://upload.wikimedia.org/wikipedia/commons/3/3e/100_zl_obverse.jpg'},
            {'v': '200 Zł', 't': 'banknote', 'u': 'https://upload.wikimedia.org/wikipedia/commons/4/4e/200_zl_obverse.jpg'}
        ],
        'THB': [
            {'v': '20 Baht', 't': 'banknote', 'u': 'https://upload.wikimedia.org/wikipedia/commons/thumb/0/0c/20_Thai_baht_2022_obverse.jpg/320px-20_Thai_baht_2022_obverse.jpg'},
            {'v': '50 Baht', 't': 'banknote', 'u': 'https://upload.wikimedia.org/wikipedia/commons/thumb/a/a4/50_Thai_baht_2022_obverse.jpg/320px-50_Thai_baht_2022_obverse.jpg'},
            {'v': '100 Baht', 't': 'banknote', 'u': 'https://upload.wikimedia.org/wikipedia/commons/thumb/4/4e/100_Thai_baht_2022_obverse.jpg/320px-100_Thai_baht_2022_obverse.jpg'}
        ],
        'USD': [
            {'v': '1 Dollar', 't': 'banknote', 'u': 'https://upload.wikimedia.org/wikipedia/commons/7/7b/United_States_one_dollar_bill%2C_obverse.jpg'},
            {'v': '5 Dollars', 't': 'banknote', 'u': 'https://upload.wikimedia.org/wikipedia/commons/4/4d/US_%245_Series_2006_obverse.jpg'},
            {'v': '20 Dollars', 't': 'banknote', 'u': 'https://upload.wikimedia.org/wikipedia/commons/b/bf/US_%2420_Series_2006_obverse.jpg'}
        ],
        'EUR': [
            {'v': '5 Euro', 't': 'banknote', 'u': 'https://upload.wikimedia.org/wikipedia/commons/thumb/5/59/EUR_5_obverse_%282013_issue%29.jpg/320px-EUR_5_obverse_%282013_issue%29.jpg'},
            {'v': '10 Euro', 't': 'banknote', 'u': 'https://upload.wikimedia.org/wikipedia/commons/thumb/3/33/EUR_10_obverse_%282014_issue%29.jpg/320px-EUR_10_obverse_%282014_issue%29.jpg'},
            {'v': '20 Euro', 't': 'banknote', 'u': 'https://upload.wikimedia.org/wikipedia/commons/thumb/3/3a/EUR_20_obverse_%282015_issue%29.jpg/320px-EUR_20_obverse_%282015_issue%29.jpg'}
        ]
    }
    
    # Process batch
    for iso_code in [c.currency.code.upper() for c in country_batch if c.currency]:
        if iso_code in curr_map:
            curr = curr_map[iso_code]
            db.query(models.CurrencyDenomination).filter(models.CurrencyDenomination.currency_id == curr.id).delete()
            
            # 1. Add Fallbacks
            if iso_code in FALLBACKS:
                for f in FALLBACKS[iso_code]:
                    db.add(models.CurrencyDenomination(currency_id=curr.id, value=f['v'], type=f['t'], image_url=f['u']))
            
            # 2. Add Wikidata results
            added_images = set()
            if iso_code in FALLBACKS:
                for f in FALLBACKS[iso_code]: added_images.add(f['u'])

            for r in results:
                if r.get("currCode", {}).get("value") == iso_code:
                    img = r.get("image", {}).get("value")
                    if img and img not in added_images:
                        type_l = r.get("typeLabel", {}).get("value", "").lower()
                        db.add(models.CurrencyDenomination(
                            currency_id=curr.id,
                            value=r.get("denomValue", {}).get("value", "Nominał"),
                            type="banknote" if "banknot" in type_l or "banknote" in type_l else "coin",
                            image_url=img
                        ))
                        added_images.add(img)
    
    db.commit()
    return len(results)

async def sync_all_currency_visuals(db: Session):
    countries = db.query(models.Country).all()
    batch_size = 10
    total_added = 0
    for i in range(0, len(countries), batch_size):
        batch = countries[i : i + batch_size]
        try:
            res = await sync_currency_visuals(db, batch)
            if res: total_added += res
        except: pass
        await asyncio.sleep(0.3)
    return {"success": total_added}
