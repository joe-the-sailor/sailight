"""
Materialwirtschaft-Modelle: Materialkatalog, Leuchtmittel, Verknüpfungen
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Date, Text, DECIMAL
from sqlalchemy.orm import relationship
from typing import List, Optional
from datetime import datetime

from app.database import Base


class MaterialCatalog(Base):
    """Materialkatalog"""
    __tablename__ = "material_catalog"
    
    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String(36), unique=True, index=True)
    category = Column(String(50), nullable=False, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    manufacturer = Column(String(100))
    unit = Column(String(20))
    unit_price = Column(DECIMAL(10, 2))
    lifespan = Column(Integer)  # Lebensdauer in Jahren
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Beziehungen
    lamps: List["Lamp"] = relationship(
        "Lamp",
        back_populates="material",
        cascade="all, delete-orphan"
    )
    light_point_materials: List["LightPointMaterial"] = relationship(
        "LightPointMaterial",
        back_populates="material",
        cascade="all, delete-orphan"
    )
    cabinet_materials: List["CabinetMaterial"] = relationship(
        "CabinetMaterial",
        back_populates="material",
        cascade="all, delete-orphan"
    )
    poles: List["Pole"] = relationship(
        "Pole",
        foreign_keys="[Pole.type_id]",
        back_populates="type"
    )
    circuit_groups: List["CircuitGroup"] = relationship(
        "CircuitGroup",
        foreign_keys="[CircuitGroup.cable_type_id]",
        back_populates="cable_type"
    )
    
    def __repr__(self):
        return f"<MaterialCatalog(id={self.id}, category='{self.category}', name='{self.name}')>"


class Lamp(Base):
    """Leuchtmittel"""
    __tablename__ = "lamp"
    
    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String(36), unique=True, index=True)
    material_id = Column(Integer, ForeignKey("material_catalog.id", ondelete="SET NULL"))
    identifier = Column(String(50), unique=True, index=True)
    type = Column(String(50), nullable=False)  # z.B. "LED", "Natriumdampf"
    color_temperature = Column(Integer)  # in Kelvin
    luminous_flux = Column(Integer)  # in Lumen
    wattage = Column(Integer)  # in Watt
    purchase_date = Column(Date)
    warranty_expiry = Column(Date)
    status = Column(String(20), default="new")
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Beziehungen
    material: Optional[MaterialCatalog] = relationship("MaterialCatalog", back_populates="lamps")
    light_points: List["LightPoint"] = relationship(
        "LightPoint",
        back_populates="lamp"
    )
    
    def __repr__(self):
        return f"<Lamp(id={self.id}, identifier='{self.identifier}', type='{self.type}')>"


class LightPointMaterial(Base):
    """Verknüpfung: Material an Leuchtstellen"""
    __tablename__ = "light_point_material"
    
    id = Column(Integer, primary_key=True, index=True)
    light_point_id = Column(Integer, ForeignKey("light_point.id", ondelete="CASCADE"), index=True)
    material_id = Column(Integer, ForeignKey("material_catalog.id", ondelete="CASCADE"), index=True)
    quantity = Column(Integer, default=1)
    installation_date = Column(Date)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Beziehungen
    light_point: Optional["LightPoint"] = relationship("LightPoint", back_populates="materials")
    material: Optional[MaterialCatalog] = relationship("MaterialCatalog", back_populates="light_point_materials")
    
    def __repr__(self):
        return f"<LightPointMaterial(light_point_id={self.light_point_id}, material_id={self.material_id})>"


class CabinetMaterial(Base):
    """Verknüpfung: Material an Schaltschränke"""
    __tablename__ = "cabinet_material"
    
    id = Column(Integer, primary_key=True, index=True)
    cabinet_id = Column(Integer, ForeignKey("cabinet.id", ondelete="CASCADE"), index=True)
    material_id = Column(Integer, ForeignKey("material_catalog.id", ondelete="CASCADE"), index=True)
    quantity = Column(Integer, default=1)
    installation_date = Column(Date)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Beziehungen
    cabinet: Optional["Cabinet"] = relationship("Cabinet", back_populates="materials")
    material: Optional[MaterialCatalog] = relationship("MaterialCatalog", back_populates="cabinet_materials")
    
    def __repr__(self):
        return f"<CabinetMaterial(cabinet_id={self.cabinet_id}, material_id={self.material_id})>"


# Zirkuläre Importe auflösen
from .infrastructure import Cabinet, LightPoint, CircuitGroup, Pole
