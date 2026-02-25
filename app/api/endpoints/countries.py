from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from ...database import get_db
from ... import schemas, crud

router = APIRouter()

@router.get("/", response_model=List[schemas.CountryBasic])
def get_countries(
        skip: int = 0,
        limit: int = 100,
        region: Optional[str] = None,
        db: Session = Depends(get_db)
):
    """Get list of all countries with basic info"""
    countries = crud.get_countries(db, skip=skip, limit=limit, region=region)
    return countries

@router.get("/{iso_code}", response_model=schemas.CountryDetail)
def get_country(iso_code: str, db: Session = Depends(get_db)):
    """Get detailed info for specific country (2 or 3 letter ISO code)"""
    iso_code = iso_code.upper()

    if len(iso_code) == 2:
        country = crud.get_country_by_iso2(db, iso_code)
    elif len(iso_code) == 3:
        country = crud.get_country_by_iso3(db, iso_code)
    else:
        raise HTTPException(status_code=400, detail="Invalid ISO code")

    if not country:
        raise HTTPException(status_code=404, detail="Country not found")

    return country
