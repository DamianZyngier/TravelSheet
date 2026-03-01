from sqlalchemy import Column, Integer, String, Boolean, DECIMAL, TIMESTAMP, Text, ForeignKey, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base

class Country(Base):
    __tablename__ = "countries"

    id = Column(Integer, primary_key=True, index=True)
    iso_alpha2 = Column(String(2), unique=True, nullable=False, index=True)
    iso_alpha3 = Column(String(3), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    name_pl = Column(String(255))
    name_local = Column(String(255))
    capital = Column(String(255))
    capital_pl = Column(String(255))
    continent = Column(String(50))
    region = Column(String(100))
    flag_emoji = Column(String(10))
    flag_url = Column(Text)
    population = Column(Integer)
    area = Column(DECIMAL(15, 2))
    latitude = Column(DECIMAL(10, 6))
    longitude = Column(DECIMAL(10, 6))
    timezone = Column(String(255))
    national_dish = Column(String(255))
    phone_code = Column(String(50))
    largest_cities = Column(Text) # Store as comma-separated or JSON
    ethnic_groups = Column(Text) # Store as comma-separated or JSON
    wiki_summary = Column(Text)
    national_symbols = Column(String(255)) # e.g. animal, flower
    unique_animals = Column(Text)
    unique_things = Column(Text)
    unesco_count = Column(Integer, default=0)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    
    # Dependency relationship (e.g. Martinique -> France)
    parent_id = Column(Integer, ForeignKey("countries.id"), nullable=True)
    is_independent = Column(Boolean, default=True)

    def __repr__(self):
        return f"<Country(name='{self.name}', iso2='{self.iso_alpha2}')>"

    # Relations
    parent = relationship("Country", remote_side=[id], backref="territories")
    languages = relationship("Language", back_populates="country", cascade="all, delete-orphan")
    religions = relationship("Religion", back_populates="country", cascade="all, delete-orphan")
    currency = relationship("Currency", back_populates="country", uselist=False, cascade="all, delete-orphan")
    safety = relationship("SafetyInfo", back_populates="country", uselist=False, cascade="all, delete-orphan")
    embassies = relationship("Embassy", back_populates="country", cascade="all, delete-orphan")
    entry_req = relationship("EntryRequirement", back_populates="country", uselist=False, cascade="all, delete-orphan")
    attractions = relationship("Attraction", back_populates="country", cascade="all, delete-orphan")
    unesco_places = relationship("UnescoPlace", back_populates="country", cascade="all, delete-orphan")
    practical = relationship("PracticalInfo", back_populates="country", uselist=False, cascade="all, delete-orphan")
    weather = relationship("Weather", back_populates="country", uselist=False, cascade="all, delete-orphan")
    climate = relationship("Climate", back_populates="country", cascade="all, delete-orphan")
    holidays = relationship("Holiday", back_populates="country", cascade="all, delete-orphan")
    laws_and_customs = relationship("LawAndCustom", back_populates="country", cascade="all, delete-orphan")
    costs = relationship("CostOfLiving", back_populates="country", uselist=False, cascade="all, delete-orphan")

class Language(Base):
    __tablename__ = "languages"

    id = Column(Integer, primary_key=True)
    country_id = Column(Integer, ForeignKey("countries.id", ondelete="CASCADE"))
    name = Column(String(100))
    code = Column(String(10))
    is_official = Column(Boolean, default=False)

    def __repr__(self):
        return f"<Language(name='{self.name}', code='{self.code}')>"

    country = relationship("Country", back_populates="languages")

class Currency(Base):
    __tablename__ = "currencies"

    id = Column(Integer, primary_key=True)
    country_id = Column(Integer, ForeignKey("countries.id", ondelete="CASCADE"))
    code = Column(String(3), nullable=False)
    name = Column(String(100))
    symbol = Column(String(10))
    exchange_rate_pln = Column(DECIMAL(10, 6))
    exchange_rate_eur = Column(DECIMAL(10, 6))
    exchange_rate_usd = Column(DECIMAL(10, 6))
    relative_cost = Column(String(20))
    last_updated = Column(TIMESTAMP, server_default=func.now())

    def __repr__(self):
        return f"<Currency(code='{self.code}', rate_pln={self.exchange_rate_pln})>"

    country = relationship("Country", back_populates="currency")

class SafetyInfo(Base):
    __tablename__ = "safety_info"

    id = Column(Integer, primary_key=True)
    country_id = Column(Integer, ForeignKey("countries.id", ondelete="CASCADE"))
    risk_level = Column(String(50))
    summary = Column(Text)
    risk_details = Column(Text)
    full_url = Column(Text)
    last_checked = Column(TIMESTAMP, server_default=func.now())

    def __repr__(self):
        return f"<Safety(risk='{self.risk_level}')>"

    country = relationship("Country", back_populates="safety")

class Embassy(Base):
    __tablename__ = "embassies"

    id = Column(Integer, primary_key=True)
    country_id = Column(Integer, ForeignKey("countries.id", ondelete="CASCADE"))
    type = Column(String(20))
    city = Column(String(100))
    address = Column(Text)
    phone = Column(String(50))
    emergency_phone = Column(String(50))
    email = Column(String(100))
    website = Column(Text)

    def __repr__(self):
        return f"<Embassy(type='{self.type}', city='{self.city}')>"

    country = relationship("Country", back_populates="embassies")

class EntryRequirement(Base):
    __tablename__ = "entry_requirements"

    id = Column(Integer, primary_key=True)
    country_id = Column(Integer, ForeignKey("countries.id", ondelete="CASCADE"))
    document_type = Column(String(50))
    min_validity_months = Column(Integer)
    passport_required = Column(Boolean)
    temp_passport_allowed = Column(Boolean)
    id_card_allowed = Column(Boolean)
    visa_required = Column(Boolean)
    visa_status = Column(String(255)) # Detailed status: "Niepotrzebna", "e-Visa", etc.
    visa_on_arrival = Column(Boolean)
    visa_free_days = Column(Integer)
    visa_notes = Column(Text)
    special_requirements = Column(Text) # Comma separated or JSON string

    country = relationship("Country", back_populates="entry_req")

class Attraction(Base):
    __tablename__ = "attractions"

    id = Column(Integer, primary_key=True)
    country_id = Column(Integer, ForeignKey("countries.id", ondelete="CASCADE"))
    name = Column(String(255), nullable=False)
    city = Column(String(100))
    description = Column(Text)
    category = Column(String(50))
    is_must_see = Column(Boolean, default=False)
    is_unique = Column(Boolean, default=False)
    display_order = Column(Integer, default=0)

    def __repr__(self):
        return f"<Attraction(name='{self.name}', cat='{self.category}')>"

    country = relationship("Country", back_populates="attractions")

class UnescoPlace(Base):
    __tablename__ = "unesco_places"

    id = Column(Integer, primary_key=True)
    country_id = Column(Integer, ForeignKey("countries.id", ondelete="CASCADE"))
    unesco_id = Column(String(20)) # Official UNESCO ID
    name = Column(String(255), nullable=False)
    description = Column(Text)
    category = Column(String(50)) # Cultural, Natural, Mixed
    is_danger = Column(Boolean, default=False)
    is_transnational = Column(Boolean, default=False)
    year = Column(Integer) # Year of inscription
    image_url = Column(String(500))

    def __repr__(self):
        return f"<UnescoPlace(name='{self.name}', cat='{self.category}')>"

    country = relationship("Country", back_populates="unesco_places")

class Religion(Base):
    __tablename__ = "religions"

    id = Column(Integer, primary_key=True)
    country_id = Column(Integer, ForeignKey("countries.id", ondelete="CASCADE"))
    name = Column(String(100))
    percentage = Column(DECIMAL(5, 2))

    country = relationship("Country", back_populates="religions")

class Holiday(Base):
    __tablename__ = "holidays"

    id = Column(Integer, primary_key=True)
    country_id = Column(Integer, ForeignKey("countries.id", ondelete="CASCADE"))
    name = Column(String(255))
    name_local = Column(String(255))
    date = Column(Date)
    type = Column(String(50)) # Public, Religious, etc.

    def __repr__(self):
        return f"<Holiday(name='{self.name}', date={self.date})>"

    country = relationship("Country", back_populates="holidays")

class PracticalInfo(Base):
    __tablename__ = "practical_info"

    id = Column(Integer, primary_key=True)
    country_id = Column(Integer, ForeignKey("countries.id", ondelete="CASCADE"), unique=True)
    tap_water_safe = Column(Boolean)
    tap_water_notes = Column(Text)
    plug_types = Column(String(50)) # e.g. "C,E"
    voltage = Column(Integer) # e.g. 230
    frequency = Column(Integer) # e.g. 50
    card_acceptance = Column(String(50)) # e.g. "high", "medium", "low"
    cash_vs_card_notes = Column(Text)
    driving_side = Column(String(10)) # "left" or "right"
    license_required = Column(String(100)) # "national" or "international"
    driving_notes = Column(Text)
    odyseusz_url = Column(Text, default="https://odyseusz.msz.gov.pl")
    store_hours = Column(Text)
    tipping_culture = Column(Text)
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

    @property
    def emergency(self):
        import json
        if self.emergency_numbers:
            try:
                return json.loads(self.emergency_numbers)
            except:
                return None
        return None

    def __repr__(self):
        return f"<PracticalInfo(country_id={self.country_id}, plugs='{self.plug_types}')>"

    country = relationship("Country", back_populates="practical")

class Weather(Base):
    __tablename__ = "weather"

    id = Column(Integer, primary_key=True)
    country_id = Column(Integer, ForeignKey("countries.id", ondelete="CASCADE"), unique=True)
    temp_c = Column(DECIMAL(4, 1))
    feels_like_c = Column(DECIMAL(4, 1))
    condition = Column(String(100))
    condition_icon = Column(String(100))
    humidity = Column(Integer)
    wind_kph = Column(DECIMAL(5, 1))
    last_updated = Column(TIMESTAMP, server_default=func.now())

    country = relationship("Country", back_populates="weather")

class Climate(Base):
    __tablename__ = "climate"

    id = Column(Integer, primary_key=True)
    country_id = Column(Integer, ForeignKey("countries.id", ondelete="CASCADE"))
    month = Column(Integer) # 1-12
    avg_temp_min = Column(Integer)
    avg_temp_max = Column(Integer)
    avg_rain_mm = Column(Integer)
    season_type = Column(String(50)) # "dry", "wet", "shoulder"

    country = relationship("Country", back_populates="climate")

class LawAndCustom(Base):
    __tablename__ = "laws_and_customs"

    id = Column(Integer, primary_key=True)
    country_id = Column(Integer, ForeignKey("countries.id", ondelete="CASCADE"))
    category = Column(String(50)) # "law", "custom", "tip", "souvenir"
    title = Column(String(255))
    description = Column(Text)

    def __repr__(self):
        return f"<LawAndCustom(cat='{self.category}', title='{self.title[:20]}...')>"

    country = relationship("Country", back_populates="laws_and_customs")

class CostOfLiving(Base):
    __tablename__ = "cost_of_living"

    id = Column(Integer, primary_key=True)
    country_id = Column(Integer, ForeignKey("countries.id", ondelete="CASCADE"), unique=True)
    
    # Indices (usually relative to NY=100)
    index_overall = Column(DECIMAL(10, 2))
    index_restaurants = Column(DECIMAL(10, 2))
    index_groceries = Column(DECIMAL(10, 2))
    index_transport = Column(DECIMAL(10, 2))
    index_accommodation = Column(DECIMAL(10, 2))
    
    # Comparison to Poland (calculated during sync)
    # 1.0 means same as Poland, 1.2 means 20% more expensive
    ratio_to_poland = Column(DECIMAL(10, 2))
    
    # Estimates in PLN
    daily_budget_low = Column(DECIMAL(10, 2)) # hostel, street food, transport
    daily_budget_mid = Column(DECIMAL(10, 2)) # budget hotel, casual dining
    daily_budget_high = Column(DECIMAL(10, 2)) # mid-range hotel, restaurant, attractions
    
    last_updated = Column(TIMESTAMP, server_default=func.now())

    country = relationship("Country", back_populates="costs")
