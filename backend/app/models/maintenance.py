"""
Wartungs-Modelle: Störungs-Typen, Status, Störungsmeldungen
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Date, Text
from sqlalchemy.orm import relationship
from typing import List, Optional
from datetime import datetime

from app.database import Base, GeometryColumn


class IncidentType(Base):
    """Störungs-Typ"""
    __tablename__ = "incident_type"
    
    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String(36), unique=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text)
    severity = Column(String(20), default="medium")  # low, medium, high, critical
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Beziehungen
    incidents: List["Incident"] = relationship(
        "Incident",
        back_populates="incident_type",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self):
        return f"<IncidentType(id={self.id}, name='{self.name}', severity='{self.severity}')>"


class IncidentStatus(Base):
    """Störungs-Status"""
    __tablename__ = "incident_status"
    
    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String(36), unique=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Beziehungen
    incidents: List["Incident"] = relationship(
        "Incident",
        back_populates="incident_status",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self):
        return f"<IncidentStatus(id={self.id}, name='{self.name}')>"


class Incident(Base):
    """Störungsmeldung"""
    __tablename__ = "incident"
    
    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String(36), unique=True, index=True)
    incident_type_id = Column(Integer, ForeignKey("incident_type.id", ondelete="SET NULL"), index=True)
    incident_status_id = Column(Integer, ForeignKey("incident_status.id", ondelete="SET NULL"), index=True)
    light_point_id = Column(Integer, ForeignKey("light_point.id", ondelete="SET NULL"), index=True)
    pole_id = Column(Integer, ForeignKey("pole.id", ondelete="SET NULL"), index=True)
    cabinet_id = Column(Integer, ForeignKey("cabinet.id", ondelete="SET NULL"), index=True)
    circuit_group_id = Column(Integer, ForeignKey("circuit_group.id", ondelete="SET NULL"), index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    geom = GeometryColumn.point()
    reported_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    reported_by = Column(Integer, ForeignKey("user_table.id", ondelete="SET NULL"))
    assigned_to = Column(Integer, ForeignKey("user_table.id", ondelete="SET NULL"))
    priority = Column(String(20), default="medium")  # low, medium, high, critical
    resolution_deadline = Column(DateTime)
    resolved_at = Column(DateTime)
    resolved_by = Column(Integer, ForeignKey("user_table.id", ondelete="SET NULL"))
    root_cause = Column(Text)
    solution = Column(Text)
    cost = Column(DECIMAL(10, 2))  # Kosten in €
    is_accident = Column(Boolean, default=False)
    accident_report_number = Column(String(50))
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Beziehungen
    incident_type: Optional[IncidentType] = relationship("IncidentType", back_populates="incidents")
    incident_status: Optional[IncidentStatus] = relationship("IncidentStatus", back_populates="incidents")
    light_point: Optional["LightPoint"] = relationship("LightPoint", foreign_keys=[light_point_id], back_populates="incidents")
    pole: Optional["Pole"] = relationship("Pole", foreign_keys=[pole_id], back_populates="incidents")
    cabinet: Optional["Cabinet"] = relationship("Cabinet", foreign_keys=[cabinet_id], back_populates="incidents")
    circuit_group: Optional["CircuitGroup"] = relationship("CircuitGroup", foreign_keys=[circuit_group_id], back_populates="incidents")
    reported_by_user: Optional["User"] = relationship("User", foreign_keys=[reported_by], back_populates="reported_incidents")
    assigned_to_user: Optional["User"] = relationship("User", foreign_keys=[assigned_to], back_populates="assigned_incidents")
    resolved_by_user: Optional["User"] = relationship("User", foreign_keys=[resolved_by], back_populates="resolved_incidents")
    documents: List["Document"] = relationship(
        "Document",
        foreign_keys="[Document.incident_id]",
        back_populates="incident"
    )
    project_infrastructures: List["ProjectInfrastructure"] = relationship(
        "ProjectInfrastructure",
        foreign_keys="[ProjectInfrastructure.incident_id]",
        back_populates="incident"
    )
    
    def __repr__(self):
        return f"<Incident(id={self.id}, title='{self.title}', status='{self.incident_status.name if self.incident_status else 'unknown'}')>"
    
    @property
    def is_open(self) -> bool:
        """Ist die Störung noch offen?"""
        if not self.incident_status:
            return True
        return self.incident_status.name not in ["Erledigt", "Storniert"]
    
    @property
    def is_overdue(self) -> bool:
        """Ist die Störung überfällig?"""
        if not self.resolution_deadline:
            return False
        return self.resolution_deadline < datetime.utcnow() and self.is_open


# Zirkuläre Importe auflösen
from .infrastructure import Cabinet, CircuitGroup, Pole, LightPoint
from .user import User
from .document import Document
from .project import ProjectInfrastructure
