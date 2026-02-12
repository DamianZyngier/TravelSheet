from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, date

class LanguageSchema(BaseModel):
    name: str
    code: Optional[str]
    is_official: bool

    class Config:
        from_attributes = True

class CurrencySchema(BaseModel):
    code: str
    name: Optional[str]
    symbol: Optional[str]
    exchange_rate_pln: Optional[float]
    exchange_rate_eur: Optional[float]
    exchange_rate_usd: Optional[float]
    relative_cost: Optional[str]
    last_updated: Optional[datetime]

    class Config:
        from_attributes = True

class SafetySchema(BaseModel):
    risk_level: Optional[str]
    summary: Optional[str]
    full_url: Optional[str]
    last_checked: Optional[datetime]

    class Config:
        from_attributes = True

class EmbassySchema(BaseModel):
    type: str
    city: str
    address: Optional[str]
    phone: Optional[str]
    emergency_phone: Optional[str]
    email: Optional[str]
    website: Optional[str]

    class Config:
        from_attributes = True

class AttractionSchema(BaseModel):
    name: str
    city: Optional[str]
    description: Optional[str]
    category: Optional[str]
    is_must_see: bool
    is_unique: bool

    class Config:
        from_attributes = True

# Basic response (lista krajów)
class CountryBasic(BaseModel):
    iso_alpha2: str
    iso_alpha3: str
    name: str
    capital: Optional[str]
    region: Optional[str]
    flag_emoji: Optional[str]
    flag_url: Optional[str]

    class Config:
        from_attributes = True

# Detailed response (pojedynczy kraj)
class CountryDetail(BaseModel):
    iso_alpha2: str
    iso_alpha3: str
    name: str
    name_local: Optional[str]
    capital: Optional[str]
    continent: Optional[str]
    region: Optional[str]
    flag_emoji: Optional[str]
    flag_url: Optional[str]
    population: Optional[int]

    languages: List[LanguageSchema] = []
    currency: Optional[CurrencySchema]
    safety: Optional[SafetySchema]
    embassies: List[EmbassySchema] = []
    attractions: List[AttractionSchema] = []

    class Config:
        from_attributes = True
