"""
Dokumentenmanagement-Modelle: Dokumenten-Typen, Dokumente
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Date, Text, BIGINT
from sqlalchemy.orm import relationship
from typing import List, Optional
from datetime import datetime

from app.database import Base


class DocumentType(Base):
    """Dokumenten-Typ"""
    __tablename__ = "document_type"
    
    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String(36), unique=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Beziehungen
    documents: List["Document"] = relationship(
        "Document",
        back_populates="document_type",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self):
        return f"<DocumentType(id={self.id}, name='{self.name}')>"


class Document(Base):
    """Dokument"""
    __tablename__ = "document"
    
    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String(36), unique=True, index=True)
    document_type_id = Column(Integer, ForeignKey("document_type.id", ondelete="SET NULL"), index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    file_path = Column(String(500), nullable=False)
    file_name = Column(String(255), nullable=False)
    file_size = Column(BIGINT)
    mime_type = Column(String(100))
    uploaded_by = Column(Integer, ForeignKey("user_table.id", ondelete="SET NULL"))
    uploaded_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Fremdschlüssel für Verknüpfungen (können NULL sein)
    light_point_id = Column(Integer, ForeignKey("light_point.id", ondelete="CASCADE"), index=True)
    pole_id = Column(Integer, ForeignKey("pole.id", ondelete="CASCADE"), index=True)
    cabinet_id = Column(Integer, ForeignKey("cabinet.id", ondelete="CASCADE"), index=True)
    circuit_group_id = Column(Integer, ForeignKey("circuit_group.id", ondelete="CASCADE"), index=True)
    incident_id = Column(Integer, ForeignKey("incident.id", ondelete="CASCADE"), index=True)
    project_id = Column(Integer, ForeignKey("project.id", ondelete="CASCADE"), index=True)
    invoice_id = Column(Integer, ForeignKey("invoice.id", ondelete="CASCADE"), index=True)
    
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Beziehungen
    document_type: Optional[DocumentType] = relationship("DocumentType", back_populates="documents")
    uploaded_by_user: Optional["User"] = relationship("User", foreign_keys=[uploaded_by], back_populates="uploaded_documents")
    light_point: Optional["LightPoint"] = relationship("LightPoint", foreign_keys=[light_point_id], back_populates="documents")
    pole: Optional["Pole"] = relationship("Pole", foreign_keys=[pole_id], back_populates="documents")
    cabinet: Optional["Cabinet"] = relationship("Cabinet", foreign_keys=[cabinet_id], back_populates="documents")
    circuit_group: Optional["CircuitGroup"] = relationship("CircuitGroup", foreign_keys=[circuit_group_id], back_populates="documents")
    incident: Optional["Incident"] = relationship("Incident", foreign_keys=[incident_id], back_populates="documents")
    project: Optional["Project"] = relationship("Project", foreign_keys=[project_id], back_populates="documents")
    invoice: Optional["Invoice"] = relationship("Invoice", foreign_keys=[invoice_id], back_populates="documents")
    
    def __repr__(self):
        return f"<Document(id={self.id}, title='{self.title}', file_name='{self.file_name}')>"
    
    @property
    def file_size_mb(self) -> float:
        """Dateigröße in MB"""
        if self.file_size:
            return float(self.file_size) / (1024 * 1024)
        return 0.0
    
    @property
    def extension(self) -> str:
        """Dateiendung"""
        if self.file_name:
            return self.file_name.split(".")[-1].lower()
        return ""
    
    @property
    def is_image(self) -> bool:
        """Ist es ein Bild?"""
        image_extensions = ["jpg", "jpeg", "png", "gif", "bmp", "svg", "webp"]
        return self.extension in image_extensions
    
    @property
    def is_pdf(self) -> bool:
        """Ist es eine PDF-Datei?"""
        return self.extension == "pdf"


# Zirkuläre Importe auflösen
from .user import User
from .infrastructure import Cabinet, CircuitGroup, Pole, LightPoint
from .maintenance import Incident
from .project import Project
from .energy import Invoice
