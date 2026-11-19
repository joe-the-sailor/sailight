"""
Infrastruktur-Modelle: Schaltschränke, Leitungsgruppen, Masten, Leuchtstellen
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Date, Text, func, DECIMAL
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property
from geoalchemy2 import Geometry
from typing import List, Optional
from datetime import datetime
from enum import Enum

from app.database import Base, GeometryColumn


class CabinetStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    MAINTENANCE = "maintenance"


class CircuitGroupStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    FAULTY = "faulty"


class PoleStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    DAMAGED = "damaged"


class LightPointStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    FAULTY = "faulty"
    MAINTENANCE = "maintenance"


class Cabinet(Base):
    """Schaltschrank"""
    __tablename__ = "cabinet"
    
    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String(36), unique=True, index=True)
    name = Column(String(100), nullable=False)
    identifier = Column(String(50), unique=True, nullable=False, index=True)
    street_id = Column(Integer, ForeignKey("street.id", ondelete="SET NULL"), index=True)
    geom = GeometryColumn.point()
    status = Column(String(20), default="active")
    voltage_level = Column(String(20))
    installation_date = Column(Date)
    responsible_user_id = Column(Integer, ForeignKey("user_table.id", ondelete="SET NULL"))
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Beziehungen
    street: Optional["Street"] = relationship("Street", back_populates="cabinets")
    circuit_groups: List["CircuitGroup"] = relationship(
        "CircuitGroup", 
        back_populates="cabinet", 
        cascade="all, delete-orphan"
    )
    electric_meters: List["ElectricMeter"] = relationship(
        "ElectricMeter",
        back_populates="cabinet",
        cascade="all, delete-orphan"
    )
    materials: List["CabinetMaterial"] = relationship(
        "CabinetMaterial",
        back_populates="cabinet",
        cascade="all, delete-orphan"
    )
    documents: List["Document"] = relationship(
        "Document",
        foreign_keys="[Document.cabinet_id]",
        back_populates="cabinet"
    )
    incidents: List["Incident"] = relationship(
        "Incident",
        foreign_keys="[Incident.cabinet_id]",
        back_populates="cabinet"
    )
    responsible_user: Optional["User"] = relationship("User", foreign_keys=[responsible_user_id], back_populates="responsible_cabinets")
    project_infrastructures: List["ProjectInfrastructure"] = relationship(
        "ProjectInfrastructure",
        foreign_keys="[ProjectInfrastructure.cabinet_id]",
        back_populates="cabinet"
    )
    audit_logs: List["AuditLog"] = relationship(
        "AuditLog",
        foreign_keys="[AuditLog.record_id]",
        primaryjoin="and_(AuditLog.table_name=='cabinet', foreign(Cabinet.id)==AuditLog.record_id)",
        viewonly=True
    )
    
    def __repr__(self):
        return f"<Cabinet(id={self.id}, identifier='{self.identifier}', name='{self.name}')>"
    
    @hybrid_property
    def circuit_group_count(self) -> int:
        """Anzahl der Leitungsgruppen"""
        return len(self.circuit_groups) if self.circuit_groups else 0
    
    @hybrid_property
    def light_point_count(self) -> int:
        """Anzahl der Leuchtstellen (über alle Leitungsgruppen)"""
        count = 0
        for cg in self.circuit_groups:
            count += len(cg.light_points) if cg.light_points else 0
        return count


class CircuitGroup(Base):
    """Leitungsgruppe (Abgang)"""
    __tablename__ = "circuit_group"
    
    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String(36), unique=True, index=True)
    cabinet_id = Column(Integer, ForeignKey("cabinet.id", ondelete="CASCADE"), index=True)
    name = Column(String(100), nullable=False)
    identifier = Column(String(50), unique=True, nullable=False, index=True)
    phase = Column(String(10))
    fuse_rating = Column(Integer)
    cable_type_id = Column(Integer, ForeignKey("material_catalog.id", ondelete="SET NULL"))
    cable_length = Column(DECIMAL(10, 2))
    status = Column(String(20), default="active")
    installation_date = Column(Date)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Beziehungen
    cabinet: Optional[Cabinet] = relationship("Cabinet", back_populates="circuit_groups")
    light_points: List["LightPoint"] = relationship(
        "LightPoint",
        back_populates="circuit_group",
        cascade="all, delete-orphan"
    )
    cable_type: Optional["MaterialCatalog"] = relationship("MaterialCatalog")
    documents: List["Document"] = relationship(
        "Document",
        foreign_keys="[Document.circuit_group_id]",
        back_populates="circuit_group"
    )
    incidents: List["Incident"] = relationship(
        "Incident",
        foreign_keys="[Incident.circuit_group_id]",
        back_populates="circuit_group"
    )
    project_infrastructures: List["ProjectInfrastructure"] = relationship(
        "ProjectInfrastructure",
        foreign_keys="[ProjectInfrastructure.circuit_group_id]",
        back_populates="circuit_group"
    )
    audit_logs: List["AuditLog"] = relationship(
        "AuditLog",
        foreign_keys="[AuditLog.record_id]",
        primaryjoin="and_(AuditLog.table_name=='circuit_group', foreign(CircuitGroup.id)==AuditLog.record_id)",
        viewonly=True
    )
    
    def __repr__(self):
        return f"<CircuitGroup(id={self.id}, identifier='{self.identifier}', cabinet_id={self.cabinet_id})>"
    
    @hybrid_property
    def light_point_count(self) -> int:
        """Anzahl der Leuchtstellen"""
        return len(self.light_points) if self.light_points else 0


class Pole(Base):
    """Mast"""
    __tablename__ = "pole"
    
    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String(36), unique=True, index=True)
    street_id = Column(Integer, ForeignKey("street.id", ondelete="SET NULL"), index=True)
    identifier = Column(String(50), unique=True, nullable=False, index=True)
    geom = GeometryColumn.point()
    height = Column(DECIMAL(5, 2))
    type_id = Column(Integer, ForeignKey("material_catalog.id", ondelete="SET NULL"))
    material = Column(String(50))
    installation_date = Column(Date)
    status = Column(String(20), default="active")
    owner = Column(String(100))
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Beziehungen
    street: Optional["Street"] = relationship("Street", back_populates="poles")
    type: Optional["MaterialCatalog"] = relationship("MaterialCatalog")
    light_points: List["LightPoint"] = relationship(
        "LightPoint",
        back_populates="pole",
        cascade="all, delete-orphan"
    )
    documents: List["Document"] = relationship(
        "Document",
        foreign_keys="[Document.pole_id]",
        back_populates="pole"
    )
    incidents: List["Incident"] = relationship(
        "Incident",
        foreign_keys="[Incident.pole_id]",
        back_populates="pole"
    )
    project_infrastructures: List["ProjectInfrastructure"] = relationship(
        "ProjectInfrastructure",
        foreign_keys="[ProjectInfrastructure.pole_id]",
        back_populates="pole"
    )
    audit_logs: List["AuditLog"] = relationship(
        "AuditLog",
        foreign_keys="[AuditLog.record_id]",
        primaryjoin="and_(AuditLog.table_name=='pole', foreign(Pole.id)==AuditLog.record_id)",
        viewonly=True
    )
    
    def __repr__(self):
        return f"<Pole(id={self.id}, identifier='{self.identifier}')>"
    
    @hybrid_property
    def light_point_count(self) -> int:
        """Anzahl der Leuchtstellen am Mast"""
        return len(self.light_points) if self.light_points else 0


class LightPoint(Base):
    """Leuchtstelle (POI)"""
    __tablename__ = "light_point"
    
    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String(36), unique=True, index=True)
    circuit_group_id = Column(Integer, ForeignKey("circuit_group.id", ondelete="SET NULL"), index=True)
    pole_id = Column(Integer, ForeignKey("pole.id", ondelete="SET NULL"), index=True)
    identifier = Column(String(50), unique=True, nullable=False, index=True)
    geom = GeometryColumn.point()
    status = Column(String(20), default="active")
    lamp_id = Column(Integer, ForeignKey("lamp.id", ondelete="SET NULL"))
    lamp_count = Column(Integer, default=1)
    mounting_height = Column(DECIMAL(5, 2))
    orientation = Column(String(20))
    light_type = Column(String(50))
    power = Column(Integer)
    installation_date = Column(Date)
    last_maintenance_date = Column(Date)
    next_maintenance_date = Column(Date)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Beziehungen
    circuit_group: Optional[CircuitGroup] = relationship("CircuitGroup", back_populates="light_points")
    pole: Optional[Pole] = relationship("Pole", back_populates="light_points")
    lamp: Optional["Lamp"] = relationship("Lamp")
    materials: List["LightPointMaterial"] = relationship(
        "LightPointMaterial",
        back_populates="light_point",
        cascade="all, delete-orphan"
    )
    documents: List["Document"] = relationship(
        "Document",
        foreign_keys="[Document.light_point_id]",
        back_populates="light_point"
    )
    incidents: List["Incident"] = relationship(
        "Incident",
        foreign_keys="[Incident.light_point_id]",
        back_populates="light_point"
    )
    project_infrastructures: List["ProjectInfrastructure"] = relationship(
        "ProjectInfrastructure",
        foreign_keys="[ProjectInfrastructure.light_point_id]",
        back_populates="light_point"
    )
    audit_logs: List["AuditLog"] = relationship(
        "AuditLog",
        foreign_keys="[AuditLog.record_id]",
        primaryjoin="and_(AuditLog.table_name=='light_point', foreign(LightPoint.id)==AuditLog.record_id)",
        viewonly=True
    )
    
    def __repr__(self):
        return f"<LightPoint(id={self.id}, identifier='{self.identifier}')>"
    
    @hybrid_property
    def full_identifier(self) -> str:
        """Vollständige Identifikation"""
        parts = []
        if self.circuit_group:
            parts.append(self.circuit_group.identifier)
        if self.pole:
            parts.append(self.pole.identifier)
        parts.append(self.identifier)
        return " - ".join(parts)
    
    @hybrid_property
    def location_description(self) -> str:
        """Beschreibung des Standorts"""
        if self.pole and self.pole.street:
            return f"{self.pole.street.name}, {self.pole.street.municipality.name if self.pole.street.municipality else ''}"
        return "Unbekannter Standort"


# Zirkuläre Importe auflösen
from sqlalchemy.orm import backref
from sqlalchemy.ext.hybrid import hybrid_property
from .geography import Street
from .user import User
from .material import MaterialCatalog, Lamp, LightPointMaterial, CabinetMaterial
from .energy import ElectricMeter
from .maintenance import Incident
from .project import ProjectInfrastructure
from .document import Document
from .audit import AuditLog

# Beziehungen nachträglich setzen
CircuitGroup.cabinet = relationship("Cabinet", back_populates="circuit_groups")
LightPoint.circuit_group = relationship("CircuitGroup", back_populates="light_points")
LightPoint.pole = relationship("Pole", back_populates="light_points")
