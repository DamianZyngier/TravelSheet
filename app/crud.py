from sqlalchemy.orm import Session
from typing import List, Optional
from . import models

def get_countries(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        region: Optional[str] = None
) -> List[models.Country]:
    query = db.query(models.Country)

    if region:
        query = query.filter(models.Country.region == region)

    return query.offset(skip).limit(limit).all()

def get_country_by_iso2(db: Session, iso_alpha2: str) -> Optional[models.Country]:
    return db.query(models.Country).filter(
        models.Country.iso_alpha2 == iso_alpha2.upper()
    ).first()

def get_country_by_iso3(db: Session, iso_alpha3: str) -> Optional[models.Country]:
    return db.query(models.Country).filter(
        models.Country.iso_alpha3 == iso_alpha3.upper()
    ).first()

def create_country(db: Session, country_data: dict) -> models.Country:
    country = models.Country(**country_data)
    db.add(country)
    db.commit()
    db.refresh(country)
    return country

def update_currency(db: Session, country_id: int, rates: dict):
    currency = db.query(models.Currency).filter(
        models.Currency.country_id == country_id
    ).first()

    if currency:
        currency.exchange_rate_pln = rates.get('PLN')
        currency.exchange_rate_eur = rates.get('EUR')
        currency.exchange_rate_usd = rates.get('USD')
        currency.last_updated = func.now()

    db.commit()
