"""
Pydantic-Schemas für Dokumentenmanagement
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class DocumentTypeBase(BaseModel):
    """Basis-Schema für Dokumenten-Typen"""
    name: str = Field(..., min_length=1, max_length=100, description="Name")
    description: Optional[str] = Field(default=None, description="Beschreibung")
    is_active: bool = Field(default=True, description="Ist aktiv?")


class DocumentTypeCreate(DocumentTypeBase):
    """Schema zum Erstellen eines Dokumenten-Typs"""
    pass


class DocumentTypeUpdate(BaseModel):
    """Schema zum Aktualisieren eines Dokumenten-Typs"""
    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    description: Optional[str] = Field(default=None)
    is_active: Optional[bool] = Field(default=None)


class DocumentTypeResponse(DocumentTypeBase):
    """Response-Schema für Dokumenten-Typen"""
    id: int
    uuid: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class DocumentBase(BaseModel):
    """Basis-Schema für Dokumente"""
    document_type_id: int = Field(..., description="Dokumenten-Typ-ID")
    title: str = Field(..., min_length=1, max_length=200, description="Titel")
    description: Optional[str] = Field(default=None, description="Beschreibung")


class DocumentCreate(DocumentBase):
    """Schema zum Erstellen eines Dokuments"""
    pass


class DocumentUpdate(BaseModel):
    """Schema zum Aktualisieren eines Dokuments"""
    document_type_id: Optional[int] = Field(default=None)
    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = Field(default=None)
    notes: Optional[str] = Field(default=None)


class DocumentResponse(DocumentBase):
    """Response-Schema für Dokumente"""
    id: int
    uuid: str
    file_path: str
    file_name: str
    file_size: int
    file_size_mb: float
    mime_type: str
    extension: str
    is_image: bool
    is_pdf: bool
    uploaded_by: int
    uploaded_at: datetime
    created_at: datetime
    document_type: Optional[dict] = None
    uploaded_by_user: Optional[dict] = None
    light_point: Optional[dict] = None
    pole: Optional[dict] = None
    cabinet: Optional[dict] = None
    circuit_group: Optional[dict] = None
    incident: Optional[dict] = None
    project: Optional[dict] = None
    invoice: Optional[dict] = None
    notes: Optional[str] = None
    
    class Config:
        from_attributes = True
