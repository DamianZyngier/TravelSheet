from sqlalchemy import Column, Integer, String, Boolean, DECIMAL, TIMESTAMP, Text, ARRAY, ForeignKey, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base

class Country(Base):
    __tablename__ = "countries"

    id = Column(Integer, primary_key=True, index=True)
    iso_alpha2 = Column(String(2), unique=True, nullable=False, index=True)
    iso_alpha3 = Column(String(3), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    name_local = Column(String(255))
    capital = Column(String(255))
    continent = Column(String(50))
    region = Column(String(100))
    flag_emoji = Column(String(10))
    flag_url = Column(Text)
    population = Column(Integer)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    # Relations
    languages = relationship("Language", back_populates="country", cascade="all, delete-orphan")
    religions = relationship("Religion", back_populates="country", cascade="all, delete-orphan")
    currency = relationship("Currency", back_populates="country", uselist=False, cascade="all, delete-orphan")
    safety = relationship("SafetyInfo", back_populates="country", uselist=False, cascade="all, delete-orphan")
    embassies = relationship("Embassy", back_populates="country", cascade="all, delete-orphan")
    entry_req = relationship("EntryRequirement", back_populates="country", uselist=False, cascade="all, delete-orphan")
    attractions = relationship("Attraction", back_populates="country", cascade="all, delete-orphan")

class Language(Base):
    __tablename__ = "languages"

    id = Column(Integer, primary_key=True)
    country_id = Column(Integer, ForeignKey("countries.id", ondelete="CASCADE"))
    name = Column(String(100))
    code = Column(String(10))
    is_official = Column(Boolean, default=False)

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

    country = relationship("Country", back_populates="currency")

class SafetyInfo(Base):
    __tablename__ = "safety_info"

    id = Column(Integer, primary_key=True)
    country_id = Column(Integer, ForeignKey("countries.id", ondelete="CASCADE"))
    risk_level = Column(String(50))
    summary = Column(Text)
    full_url = Column(Text)
    last_checked = Column(TIMESTAMP, server_default=func.now())

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

    country = relationship("Country", back_populates="embassies")

class EntryRequirement(Base):
    __tablename__ = "entry_requirements"

    id = Column(Integer, primary_key=True)
    country_id = Column(Integer, ForeignKey("countries.id", ondelete="CASCADE"))
    document_type = Column(String(50))
    min_validity_months = Column(Integer)
    visa_required = Column(Boolean)
    visa_on_arrival = Column(Boolean)
    visa_free_days = Column(Integer)
    visa_notes = Column(Text)
    special_requirements = Column(ARRAY(Text))

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

    country = relationship("Country", back_populates="attractions")

# Dodaj pozostałe modele analogicznie...
