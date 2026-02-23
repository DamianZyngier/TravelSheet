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
    name_pl: Optional[str]
    capital: Optional[str]
    region: Optional[str]
    flag_emoji: Optional[str]
    flag_url: Optional[str]

    class Config:
        from_attributes = True

class ReligionSchema(BaseModel):
    name: str
    percentage: Optional[float]

    class Config:
        from_attributes = True

class HolidaySchema(BaseModel):
    name: str
    name_local: Optional[str]
    date: date
    type: Optional[str]

    class Config:
        from_attributes = True

class WeatherSchema(BaseModel):
    temp_c: Optional[float]
    feels_like_c: Optional[float]
    condition: Optional[str]
    condition_icon: Optional[str]
    humidity: Optional[int]
    wind_kph: Optional[float]
    last_updated: Optional[datetime]

    class Config:
        from_attributes = True

class PracticalSchema(BaseModel):
    tap_water_safe: Optional[bool]
    tap_water_notes: Optional[str]
    plug_types: List[str] = []
    voltage: Optional[int]
    frequency: Optional[int]
    card_acceptance: Optional[str]
    cash_vs_card_notes: Optional[str]
    driving_side: Optional[str]
    license_required: Optional[str]
    driving_notes: Optional[str]
    odyseusz_url: Optional[str]
    store_hours: Optional[str]
    tipping_culture: Optional[str]
    internet_notes: Optional[str]
    esim_available: Optional[bool]

    class Config:
        from_attributes = True

class LawCustomSchema(BaseModel):
    category: str
    title: str
    description: Optional[str]

    class Config:
        from_attributes = True

# Detailed response (pojedynczy kraj)
class CountryDetail(BaseModel):
    iso_alpha2: str
    iso_alpha3: str
    name: str
    name_pl: Optional[str]
    name_local: Optional[str]
    capital: Optional[str]
    continent: Optional[str]
    region: Optional[str]
    flag_emoji: Optional[str]
    flag_url: Optional[str]
    population: Optional[int]

    # Grouped Info
    languages: List[LanguageSchema] = []
    currency: Optional[CurrencySchema]
    safety: Optional[SafetySchema]
    embassies: List[EmbassySchema] = []
    attractions: List[AttractionSchema] = []
    
    # New Fields
    religions: List[ReligionSchema] = []
    holidays: List[HolidaySchema] = []
    weather: Optional[WeatherSchema]
    practical: Optional[PracticalSchema]
    laws_and_customs: List[LawCustomSchema] = []

    class Config:
        from_attributes = True
