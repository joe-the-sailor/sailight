"""
Projekt-Modelle: Projekt-Typen, Status, Projekte, Infrastruktur-Verknüpfungen
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Date, Text, DECIMAL
from sqlalchemy.orm import relationship
from typing import List, Optional
from datetime import datetime

from app.database import Base


class ProjectType(Base):
    """Projekt-Typ"""
    __tablename__ = "project_type"
    
    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String(36), unique=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Beziehungen
    projects: List["Project"] = relationship(
        "Project",
        back_populates="project_type",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self):
        return f"<ProjectType(id={self.id}, name='{self.name}')>"


class ProjectStatus(Base):
    """Projekt-Status"""
    __tablename__ = "project_status"
    
    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String(36), unique=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Beziehungen
    projects: List["Project"] = relationship(
        "Project",
        back_populates="project_status",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self):
        return f"<ProjectStatus(id={self.id}, name='{self.name}')>"


class Project(Base):
    """Projekt"""
    __tablename__ = "project"
    
    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String(36), unique=True, index=True)
    project_type_id = Column(Integer, ForeignKey("project_type.id", ondelete="SET NULL"), index=True)
    project_status_id = Column(Integer, ForeignKey("project_status.id", ondelete="SET NULL"), index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text)
    identifier = Column(String(50), unique=True, nullable=False, index=True)
    start_date = Column(Date)
    end_date = Column(Date)
    budget = Column(DECIMAL(12, 2))  # Budget in €
    actual_cost = Column(DECIMAL(12, 2))  # Tatsächliche Kosten in €
    responsible_user_id = Column(Integer, ForeignKey("user_table.id", ondelete="SET NULL"))
    municipality_id = Column(Integer, ForeignKey("municipality.id", ondelete="SET NULL"))
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Beziehungen
    project_type: Optional[ProjectType] = relationship("ProjectType", back_populates="projects")
    project_status: Optional[ProjectStatus] = relationship("ProjectStatus", back_populates="projects")
    responsible_user: Optional["User"] = relationship("User", foreign_keys=[responsible_user_id], back_populates="responsible_projects")
    municipality: Optional["Municipality"] = relationship("Municipality", back_populates="projects")
    project_infrastructures: List["ProjectInfrastructure"] = relationship(
        "ProjectInfrastructure",
        back_populates="project",
        cascade="all, delete-orphan"
    )
    documents: List["Document"] = relationship(
        "Document",
        foreign_keys="[Document.project_id]",
        back_populates="project"
    )
    
    def __repr__(self):
        return f"<Project(id={self.id}, identifier='{self.identifier}', name='{self.name}')>"
    
    @property
    def is_active(self) -> bool:
        """Ist das Projekt aktiv?"""
        if not self.project_status:
            return False
        return self.project_status.name in ["Geplant", "Genehmigt", "In Bearbeitung"]
    
    @property
    def is_completed(self) -> bool:
        """Ist das Projekt abgeschlossen?"""
        if not self.project_status:
            return False
        return self.project_status.name == "Abgeschlossen"
    
    @property
    def budget_utilization(self) -> float:
        """Budget-Auslastung in %"""
        if not self.budget or self.budget == 0:
            return 0.0
        return (float(self.actual_cost or 0) / float(self.budget)) * 100


class ProjectInfrastructure(Base):
    """Verknüpfung: Projekt mit Infrastruktur-Elementen"""
    __tablename__ = "project_infrastructure"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("project.id", ondelete="CASCADE"), index=True)
    cabinet_id = Column(Integer, ForeignKey("cabinet.id", ondelete="CASCADE"), index=True)
    circuit_group_id = Column(Integer, ForeignKey("circuit_group.id", ondelete="CASCADE"), index=True)
    pole_id = Column(Integer, ForeignKey("pole.id", ondelete="CASCADE"), index=True)
    light_point_id = Column(Integer, ForeignKey("light_point.id", ondelete="CASCADE"), index=True)
    incident_id = Column(Integer, ForeignKey("incident.id", ondelete="CASCADE"), index=True)
    action = Column(String(50), nullable=False)  # z.B. "Neubau", "Ersatz", "Wartung"
    status = Column(String(20), default="planned")  # planned, in_progress, completed
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Beziehungen
    project: Optional[Project] = relationship("Project", back_populates="project_infrastructures")
    cabinet: Optional["Cabinet"] = relationship("Cabinet", foreign_keys=[cabinet_id], back_populates="project_infrastructures")
    circuit_group: Optional["CircuitGroup"] = relationship("CircuitGroup", foreign_keys=[circuit_group_id], back_populates="project_infrastructures")
    pole: Optional["Pole"] = relationship("Pole", foreign_keys=[pole_id], back_populates="project_infrastructures")
    light_point: Optional["LightPoint"] = relationship("LightPoint", foreign_keys=[light_point_id], back_populates="project_infrastructures")
    incident: Optional["Incident"] = relationship("Incident", foreign_keys=[incident_id], back_populates="project_infrastructures")
    
    def __repr__(self):
        return f"<ProjectInfrastructure(id={self.id}, project_id={self.project_id}, action='{self.action}')>"


# Zirkuläre Importe auflösen
from .geography import Municipality
from .user import User
from .infrastructure import Cabinet, CircuitGroup, Pole, LightPoint
from .maintenance import Incident
from .document import Document
