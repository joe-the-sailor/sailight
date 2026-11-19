"""
Benutzer- und Rollen-Modelle
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, func, Table, ForeignKey
from sqlalchemy.orm import relationship
from typing import List, Optional
from datetime import datetime

from app.database import Base


# n:m Beziehungstabelle für Benutzer-Rollen
user_role_association = Table(
    "user_role",
    Base.metadata,
    Column("id", Integer, primary_key=True, index=True),
    Column("user_id", Integer, ForeignKey("user_table.id", ondelete="CASCADE"), index=True),
    Column("role_id", Integer, ForeignKey("role.id", ondelete="CASCADE"), index=True),
    Column("created_at", DateTime, default=datetime.utcnow),
    __table_args__=(
        UniqueConstraint("user_id", "role_id", name="uq_user_role"),
    )
)


class Role(Base):
    """Rolle"""
    __tablename__ = "role"
    
    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String(36), unique=True, index=True)
    name = Column(String(50), unique=True, nullable=False, index=True)
    description = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Beziehungen
    users: List["User"] = relationship(
        "User", 
        secondary=user_role_association, 
        back_populates="roles"
    )
    
    def __repr__(self):
        return f"<Role(id={self.id}, name='{self.name}')>"


class User(Base):
    """Benutzer"""
    __tablename__ = "user_table"
    
    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String(36), unique=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(100))
    last_name = Column(String(100))
    phone = Column(String(20))
    department = Column(String(100))
    is_active = Column(Boolean, default=True)
    last_login = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Beziehungen
    roles: List[Role] = relationship(
        "Role",
        secondary=user_role_association,
        back_populates="users"
    )
    reported_incidents: List["Incident"] = relationship(
        "Incident",
        foreign_keys="[Incident.reported_by]",
        back_populates="reported_by_user"
    )
    assigned_incidents: List["Incident"] = relationship(
        "Incident",
        foreign_keys="[Incident.assigned_to]",
        back_populates="assigned_to_user"
    )
    resolved_incidents: List["Incident"] = relationship(
        "Incident",
        foreign_keys="[Incident.resolved_by]",
        back_populates="resolved_by_user"
    )
    responsible_projects: List["Project"] = relationship(
        "Project",
        foreign_keys="[Project.responsible_user_id]",
        back_populates="responsible_user"
    )
    uploaded_documents: List["Document"] = relationship(
        "Document",
        foreign_keys="[Document.uploaded_by]",
        back_populates="uploaded_by_user"
    )
    meter_readings: List["MeterReading"] = relationship(
        "MeterReading",
        foreign_keys="[MeterReading.recorded_by]",
        back_populates="recorded_by_user"
    )
    audit_logs: List["AuditLog"] = relationship(
        "AuditLog",
        foreign_keys="[AuditLog.user_id]",
        back_populates="user"
    )
    responsible_cabinets: List["Cabinet"] = relationship(
        "Cabinet",
        foreign_keys="[Cabinet.responsible_user_id]",
        back_populates="responsible_user"
    )
    
    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"
    
    @property
    def full_name(self) -> str:
        """Vollständiger Name"""
        return f"{self.first_name or ''} {self.last_name or ''}".strip()
    
    @property
    def role_names(self) -> List[str]:
        """Liste der Rollennamen"""
        return [role.name for role in self.roles]
    
    def has_role(self, role_name: str) -> bool:
        """Prüft, ob der Benutzer eine bestimmte Rolle hat"""
        return role_name in self.role_names


class UserRole(Base):
    """Benutzer-Rolle (explizites Modell für die Beziehungstabelle)"""
    __tablename__ = "user_role"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user_table.id", ondelete="CASCADE"), index=True)
    role_id = Column(Integer, ForeignKey("role.id", ondelete="CASCADE"), index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Beziehungen
    user: Optional[User] = relationship("User", backref="user_roles")
    role: Optional[Role] = relationship("Role", backref="user_roles")
    
    __table_args__ = (
        UniqueConstraint("user_id", "role_id", name="uq_user_role_explicit"),
    )
    
    def __repr__(self):
        return f"<UserRole(user_id={self.user_id}, role_id={self.role_id})>"


# Zirkuläre Importe auflösen
from sqlalchemy import UniqueConstraint
from .maintenance import Incident
from .project import Project
from .document import Document
from .energy import MeterReading
from .audit import AuditLog
from .infrastructure import Cabinet
