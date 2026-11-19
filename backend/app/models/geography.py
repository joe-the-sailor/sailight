"""
Geografische Modelle: Land, Region, Gemeinde, Straße
"""

from sqlalchemy import Column, Integer, String, DateTime, func
from sqlalchemy.orm import relationship
from geoalchemy2 import Geometry
from geoalchemy2.types import GeometryType
from typing import List, Optional
from datetime import datetime

from app.database import Base, GeometryColumn


class Country(Base):
    """Land"""
    __tablename__ = "country"
    
    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String(36), unique=True, index=True)
    name = Column(String(100), nullable=False)
    iso_code = Column(String(2), unique=True, nullable=False, index=True)
    geom = GeometryColumn.polygon()
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Beziehungen
    regions: List["Region"] = relationship("Region", back_populates="country", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Country(id={self.id}, name='{self.name}', iso_code='{self.iso_code}')>"


class Region(Base):
    """Region"""
    __tablename__ = "region"
    
    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String(36), unique=True, index=True)
    country_id = Column(Integer, ForeignKey("country.id", ondelete="CASCADE"), index=True)
    name = Column(String(100), nullable=False)
    code = Column(String(10), unique=True, index=True)
    geom = GeometryColumn.polygon()
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Beziehungen
    country: Optional[Country] = relationship("Country", back_populates="regions")
    municipalities: List["Municipality"] = relationship("Municipality", back_populates="region", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Region(id={self.id}, name='{self.name}', code='{self.code}')>"


class Municipality(Base):
    """Gemeinde"""
    __tablename__ = "municipality"
    
    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String(36), unique=True, index=True)
    region_id = Column(Integer, ForeignKey("region.id", ondelete="CASCADE"), index=True)
    name = Column(String(100), nullable=False)
    code = Column(String(10), unique=True, index=True)
    geom = GeometryColumn.polygon()
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Beziehungen
    region: Optional[Region] = relationship("Region", back_populates="municipalities")
    streets: List["Street"] = relationship("Street", back_populates="municipality", cascade="all, delete-orphan")
    projects: List["Project"] = relationship("Project", back_populates="municipality")
    
    def __repr__(self):
        return f"<Municipality(id={self.id}, name='{self.name}', code='{self.code}')>"


class Street(Base):
    """Straße"""
    __tablename__ = "street"
    
    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String(36), unique=True, index=True)
    municipality_id = Column(Integer, ForeignKey("municipality.id", ondelete="CASCADE"), index=True)
    name = Column(String(200), nullable=False)
    street_number_start = Column(Integer)
    street_number_end = Column(Integer)
    geom = GeometryColumn.linestring()
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Beziehungen
    municipality: Optional[Municipality] = relationship("Municipality", back_populates="streets")
    poles: List["Pole"] = relationship("Pole", back_populates="street")
    cabinets: List["Cabinet"] = relationship("Cabinet", back_populates="street")
    
    def __repr__(self):
        return f"<Street(id={self.id}, name='{self.name}')>"


# Zirkuläre Importe auflösen
from sqlalchemy import ForeignKey
from .infrastructure import Pole, Cabinet
from .project import Project

# Beziehungen nachträglich setzen
Region.country = relationship("Country", back_populates="regions")
Municipality.region = relationship("Region", back_populates="municipalities")
Street.municipality = relationship("Municipality", back_populates="streets")
