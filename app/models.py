from sqlalchemy import Column, Integer, String, Boolean, DECIMAL, TIMESTAMP, Text, ForeignKey, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base

class Country(Base):
    __tablename__ = "countries"

    id = Column(Integer, primary_key=True)
    iso_alpha2 = Column(String(2), unique=True, nullable=False, index=True)
    iso_alpha3 = Column(String(3), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    name_pl = Column(String(100), index=True)
    capital = Column(String(100))
    continent = Column(String(50), index=True)
    region = Column(String(100), index=True)
    flag_url = Column(String(255))
    flag_emoji = Column(String(10))
    latitude = Column(DECIMAL(10, 6))
    longitude = Column(DECIMAL(10, 6))
    population = Column(Integer)
    area = Column(DECIMAL(15, 2))
    phone_code = Column(String(20))
    
    # Wiki & Info
    wiki_summary = Column(Text)
    unesco_count = Column(Integer, default=0)
    
    # Extended Stats from Wikidata
    timezone = Column(String(100))
    national_dish = Column(Text)
    national_symbols = Column(Text) # Symbols or motto
    alcohol_status = Column(Text) # Status/rules about alcohol
    lgbtq_status = Column(Text) # Status of rights
    id_requirement = Column(Text) # If ID or passport is needed
    main_airport = Column(Text)
    railway_info = Column(Text)
    natural_hazards = Column(Text)
    popular_apps = Column(Text)
    largest_cities = Column(Text)
    ethnic_groups = Column(Text)
    climate_description = Column(Text) # General description of climate types
    unique_animals = Column(Text)
    unique_things = Column(Text)
    travel_types = Column(Text) # JSON string with travel categories and highlights
    
    # New Fields for Advanced Info
    hdi = Column(DECIMAL(10, 3))
    life_expectancy = Column(DECIMAL(10, 2))
    gdp_nominal = Column(DECIMAL(25, 2)) # Large numbers for GDP
    gdp_ppp = Column(DECIMAL(25, 2))
    gdp_per_capita = Column(DECIMAL(15, 2))
    gini = Column(DECIMAL(10, 2))
    coat_of_arms_url = Column(String(500))
    inception_date = Column(String(100))
    official_tourist_website = Column(Text)
    regional_products = Column(Text) # GI products like cheese, wine
    has_ekuz = Column(Boolean, default=False, index=True)
    
    is_independent = Column(Boolean, default=True)
    parent_id = Column(Integer, ForeignKey("countries.id"), index=True)
    
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    # Relationships
    parent = relationship("Country", remote_side=[id], back_populates="territories")
    territories = relationship("Country", back_populates="parent")
    languages = relationship("Language", back_populates="country", cascade="all, delete-orphan")
    currency = relationship("Currency", back_populates="country", uselist=False, cascade="all, delete-orphan")
    safety = relationship("SafetyInfo", back_populates="country", uselist=False, cascade="all, delete-orphan")
    embassies = relationship("Embassy", back_populates="country", cascade="all, delete-orphan")
    practical = relationship("PracticalInfo", back_populates="country", uselist=False, cascade="all, delete-orphan")
    entry_req = relationship("EntryRequirement", back_populates="country", uselist=False, cascade="all, delete-orphan")
    attractions = relationship("Attraction", back_populates="country", cascade="all, delete-orphan")
    unesco_places = relationship("UnescoPlace", back_populates="country", cascade="all, delete-orphan")
    religions = relationship("Religion", back_populates="country", cascade="all, delete-orphan")
    souvenirs = relationship("Souvenir", back_populates="country", cascade="all, delete-orphan")
    holidays = relationship("Holiday", back_populates="country", cascade="all, delete-orphan")
    weather = relationship("Weather", back_populates="country", uselist=False, cascade="all, delete-orphan")
    climate = relationship("Climate", back_populates="country", cascade="all, delete-orphan")
    costs = relationship("CostOfLiving", back_populates="country", uselist=False, cascade="all, delete-orphan")
    laws_and_customs = relationship("LawAndCustom", back_populates="country", cascade="all, delete-orphan")

class Language(Base):
    __tablename__ = "languages"

    id = Column(Integer, primary_key=True)
    country_id = Column(Integer, ForeignKey("countries.id", ondelete="CASCADE"), index=True)
    name = Column(String(100))
    code = Column(String(10))
    is_official = Column(Boolean, default=False)
    last_updated = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    country = relationship("Country", back_populates="languages")

class Currency(Base):
    __tablename__ = "currencies"

    id = Column(Integer, primary_key=True)
    country_id = Column(Integer, ForeignKey("countries.id", ondelete="CASCADE"), index=True)
    code = Column(String(3), nullable=False)
    name = Column(String(100))
    symbol = Column(String(10))
    exchange_rate_pln = Column(DECIMAL(10, 6))
    relative_cost = Column(String(20))
    last_updated = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    country = relationship("Country", back_populates="currency")
    denominations = relationship("CurrencyDenomination", back_populates="currency", cascade="all, delete-orphan")

class CurrencyDenomination(Base):
    __tablename__ = "currency_denominations"

    id = Column(Integer, primary_key=True)
    currency_id = Column(Integer, ForeignKey("currencies.id", ondelete="CASCADE"), index=True)
    value = Column(String(50))
    type = Column(String(20)) # banknote, coin
    image_url = Column(String(500))
    last_updated = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    currency = relationship("Currency", back_populates="denominations")

class SafetyInfo(Base):
    __tablename__ = "safety_info"

    id = Column(Integer, primary_key=True)
    country_id = Column(Integer, ForeignKey("countries.id", ondelete="CASCADE"), index=True)
    risk_level = Column(String(50), index=True)
    summary = Column(Text)
    risk_details = Column(Text)
    full_url = Column(Text)
    last_checked = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    country = relationship("Country", back_populates="safety")

class Embassy(Base):
    __tablename__ = "embassies"

    id = Column(Integer, primary_key=True)
    country_id = Column(Integer, ForeignKey("countries.id", ondelete="CASCADE"), index=True)
    type = Column(String(20))
    city = Column(String(100))
    address = Column(Text)
    phone = Column(String(50))
    emergency_phone = Column(String(50))
    email = Column(String(100))
    website = Column(Text)
    last_updated = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    country = relationship("Country", back_populates="embassies")

class EntryRequirement(Base):
    __tablename__ = "entry_requirements"

    id = Column(Integer, primary_key=True)
    country_id = Column(Integer, ForeignKey("countries.id", ondelete="CASCADE"), index=True)
    passport_required = Column(Boolean)
    temp_passport_allowed = Column(Boolean)
    id_card_allowed = Column(Boolean)
    visa_required = Column(Boolean)
    visa_status = Column(String(255)) # Detailed status: "Niepotrzebna", "e-Visa", etc.
    visa_notes = Column(Text)
    last_updated = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    country = relationship("Country", back_populates="entry_req")

class Attraction(Base):
    __tablename__ = "attractions"

    id = Column(Integer, primary_key=True)
    country_id = Column(Integer, ForeignKey("countries.id", ondelete="CASCADE"), index=True)
    name = Column(String(255), nullable=False)
    city = Column(String(100))
    description = Column(Text)
    category = Column(String(50))
    is_must_see = Column(Boolean, default=False)
    is_unique = Column(Boolean, default=False)
    booking_info = Column(Text) # Information about pre-booking tickets
    display_order = Column(Integer, default=0)
    last_updated = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    country = relationship("Country", back_populates="attractions")

class UnescoPlace(Base):
    __tablename__ = "unesco_places"

    id = Column(Integer, primary_key=True)
    country_id = Column(Integer, ForeignKey("countries.id", ondelete="CASCADE"), index=True)
    unesco_id = Column(String(20)) # Official UNESCO ID
    name = Column(String(255), nullable=False)
    description = Column(Text)
    category = Column(String(50)) # Cultural, Natural, Mixed
    is_danger = Column(Boolean, default=False)
    is_transnational = Column(Boolean, default=False)
    year = Column(Integer) # Year of inscription
    image_url = Column(String(500))
    last_updated = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    country = relationship("Country", back_populates="unesco_places")

class Religion(Base):
    __tablename__ = "religions"

    id = Column(Integer, primary_key=True)
    country_id = Column(Integer, ForeignKey("countries.id", ondelete="CASCADE"), index=True)
    name = Column(String(100))
    percentage = Column(DECIMAL(5, 2))
    last_updated = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    country = relationship("Country", back_populates="religions")

class Souvenir(Base):
    __tablename__ = "souvenirs"

    id = Column(Integer, primary_key=True)
    country_id = Column(Integer, ForeignKey("countries.id", ondelete="CASCADE"), index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    category = Column(String(50)) # food, handicraft, alcohol, etc.
    image_url = Column(String(500))
    last_updated = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    country = relationship("Country", back_populates="souvenirs")

class Holiday(Base):
    __tablename__ = "holidays"

    id = Column(Integer, primary_key=True)
    country_id = Column(Integer, ForeignKey("countries.id", ondelete="CASCADE"), index=True)
    name = Column(String(255))
    name_local = Column(String(255))
    date = Column(Date)
    type = Column(String(50)) # Public, Religious, etc.
    last_updated = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    country = relationship("Country", back_populates="holidays")


class PracticalInfo(Base):
    __tablename__ = "practical_info"

    id = Column(Integer, primary_key=True)
    country_id = Column(Integer, ForeignKey("countries.id", ondelete="CASCADE"), unique=True, index=True)
    tap_water_safe = Column(Boolean)
    plug_types = Column(String(50)) # e.g. "C,E"
    voltage = Column(Integer) # e.g. 230
    frequency = Column(Integer) # e.g. 50
    card_acceptance = Column(String(50)) # e.g. "high", "medium", "low"
    driving_side = Column(String(10)) # "left" or "right"
    store_hours = Column(Text)
    internet_notes = Column(Text)
    esim_available = Column(Boolean)
    emergency_numbers = Column(Text) # JSON string with police, ambulance, fire
    vaccinations_required = Column(Text)
    vaccinations_suggested = Column(Text)
    health_info = Column(Text)
    roaming_info = Column(Text) # Info about Roam Like at Home
    license_type = Column(String(255)) # Info about driving license requirements
    water_safe_for_brushing = Column(Boolean)
    best_exchange_currency = Column(String(100)) # e.g. "USD, EUR"
    exchange_where = Column(String(255)) # e.g. "Polska", "Na miejscu"
    atm_advice = Column(Text)
    bargaining_info = Column(Text) # Info if bargaining is common/advised
    
    # New cultural/law fields
    alcohol_rules = Column(Text)
    dress_code = Column(Text)
    photography_restrictions = Column(Text)
    sensitive_topics = Column(Text)
    local_norms = Column(Text)
    souvenirs = Column(Text) # Local shopping/gifts info
    
    last_updated = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    country = relationship("Country", back_populates="practical")

class Weather(Base):
    __tablename__ = "weather"

    id = Column(Integer, primary_key=True)
    country_id = Column(Integer, ForeignKey("countries.id", ondelete="CASCADE"), unique=True, index=True)
    temp_c = Column(DECIMAL(4, 1))
    feels_like_c = Column(DECIMAL(4, 1))
    condition = Column(String(100))
    condition_icon = Column(String(100))
    humidity = Column(Integer)
    wind_kph = Column(DECIMAL(5, 1))
    forecast_json = Column(Text) # JSON string with 7-day forecast
    last_updated = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    country = relationship("Country", back_populates="weather")

class Climate(Base):
    __tablename__ = "climate"

    id = Column(Integer, primary_key=True)
    country_id = Column(Integer, ForeignKey("countries.id", ondelete="CASCADE"), index=True)
    month = Column(Integer) # 1-12
    avg_temp_min = Column(Integer)
    avg_temp_max = Column(Integer)
    avg_rain_mm = Column(Integer)
    season_type = Column(String(50)) # "dry", "wet", "shoulder"
    last_updated = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    country = relationship("Country", back_populates="climate")

class LawAndCustom(Base):
    __tablename__ = "laws_and_customs"

    id = Column(Integer, primary_key=True)
    country_id = Column(Integer, ForeignKey("countries.id", ondelete="CASCADE"), index=True)
    category = Column(String(50)) # "law", "custom", "tip", "souvenir"
    title = Column(String(255))
    description = Column(Text)
    last_updated = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    country = relationship("Country", back_populates="laws_and_customs")

class CostOfLiving(Base):
    __tablename__ = "cost_of_living"

    id = Column(Integer, primary_key=True)
    country_id = Column(Integer, ForeignKey("countries.id", ondelete="CASCADE"), unique=True, index=True)
    index_overall = Column(DECIMAL(10, 2))
    index_restaurants = Column(DECIMAL(10, 2))
    index_groceries = Column(DECIMAL(10, 2))
    index_transport = Column(DECIMAL(10, 2))
    index_accommodation = Column(DECIMAL(10, 2))
    ratio_to_poland = Column(DECIMAL(10, 2))
    daily_budget_low = Column(DECIMAL(10, 2))
    daily_budget_mid = Column(DECIMAL(10, 2))
    daily_budget_high = Column(DECIMAL(10, 2))
    last_updated = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    country = relationship("Country", back_populates="costs")
