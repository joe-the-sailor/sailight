"""
Pydantic-Schemas für Wartung: Störungs-Typen, Status, Störungsmeldungen
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date
from decimal import Decimal


class IncidentTypeBase(BaseModel):
    """Basis-Schema für Störungs-Typen"""
    name: str = Field(..., min_length=1, max_length=100, description="Name")
    description: Optional[str] = Field(default=None, description="Beschreibung")
    severity: str = Field(default="medium", description="Schweregrad")
    is_active: bool = Field(default=True, description="Ist aktiv?")


class IncidentTypeCreate(IncidentTypeBase):
    """Schema zum Erstellen eines Störungs-Typs"""
    pass


class IncidentTypeUpdate(BaseModel):
    """Schema zum Aktualisieren eines Störungs-Typs"""
    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    description: Optional[str] = Field(default=None)
    severity: Optional[str] = Field(default=None)
    is_active: Optional[bool] = Field(default=None)


class IncidentTypeResponse(IncidentTypeBase):
    """Response-Schema für Störungs-Typen"""
    id: int
    uuid: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class IncidentStatusBase(BaseModel):
    """Basis-Schema für Störungs-Status"""
    name: str = Field(..., min_length=1, max_length=50, description="Name")
    description: Optional[str] = Field(default=None, description="Beschreibung")
    is_active: bool = Field(default=True, description="Ist aktiv?")


class IncidentStatusCreate(IncidentStatusBase):
    """Schema zum Erstellen eines Störungs-Status"""
    pass


class IncidentStatusUpdate(BaseModel):
    """Schema zum Aktualisieren eines Störungs-Status"""
    name: Optional[str] = Field(default=None, min_length=1, max_length=50)
    description: Optional[str] = Field(default=None)
    is_active: Optional[bool] = Field(default=None)


class IncidentStatusResponse(IncidentStatusBase):
    """Response-Schema für Störungs-Status"""
    id: int
    uuid: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class IncidentBase(BaseModel):
    """Basis-Schema für Störungsmeldungen"""
    incident_type_id: Optional[int] = Field(default=None, description="Störungs-Typ-ID")
    incident_status_id: Optional[int] = Field(default=None, description="Störungs-Status-ID")
    light_point_id: Optional[int] = Field(default=None, description="Leuchtstellen-ID")
    pole_id: Optional[int] = Field(default=None, description="Mast-ID")
    cabinet_id: Optional[int] = Field(default=None, description="Schaltschrank-ID")
    circuit_group_id: Optional[int] = Field(default=None, description="Leitungsgruppen-ID")
    title: str = Field(..., min_length=1, max_length=200, description="Titel")
    description: Optional[str] = Field(default=None, description="Beschreibung")
    geom: Optional[dict] = Field(default=None, description="Geometrie (Point)")
    priority: str = Field(default="medium", description="Priorität")
    resolution_deadline: Optional[datetime] = Field(default=None, description="Lösungsfrist")
    is_accident: bool = Field(default=False, description="Ist ein Unfall?")
    accident_report_number: Optional[str] = Field(default=None, max_length=50, description="Unfallnummer")
    notes: Optional[str] = Field(default=None, description="Notizen")


class IncidentCreate(IncidentBase):
    """Schema zum Erstellen einer Störungsmeldung"""
    pass


class IncidentUpdate(BaseModel):
    """Schema zum Aktualisieren einer Störungsmeldung"""
    incident_type_id: Optional[int] = Field(default=None)
    incident_status_id: Optional[int] = Field(default=None)
    light_point_id: Optional[int] = Field(default=None)
    pole_id: Optional[int] = Field(default=None)
    cabinet_id: Optional[int] = Field(default=None)
    circuit_group_id: Optional[int] = Field(default=None)
    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = Field(default=None)
    geom: Optional[dict] = Field(default=None)
    assigned_to: Optional[int] = Field(default=None, description="Zugewiesen an Benutzer-ID")
    priority: Optional[str] = Field(default=None)
    resolution_deadline: Optional[datetime] = Field(default=None)
    root_cause: Optional[str] = Field(default=None, description="Ursache")
    solution: Optional[str] = Field(default=None, description="Lösung")
    cost: Optional[Decimal] = Field(default=None, description="Kosten")
    is_accident: Optional[bool] = Field(default=None)
    accident_report_number: Optional[str] = Field(default=None, max_length=50)
    notes: Optional[str] = Field(default=None)


class IncidentResponse(IncidentBase):
    """Response-Schema für Störungsmeldungen"""
    id: int
    uuid: str
    reported_at: datetime
    reported_by: int
    assigned_to: Optional[int] = None
    resolved_at: Optional[datetime] = None
    resolved_by: Optional[int] = None
    root_cause: Optional[str] = None
    solution: Optional[str] = None
    cost: Optional[Decimal] = None
    created_at: datetime
    updated_at: datetime
    is_open: bool = True
    is_overdue: bool = False
    incident_type: Optional[dict] = None
    incident_status: Optional[dict] = None
    light_point: Optional[dict] = None
    pole: Optional[dict] = None
    cabinet: Optional[dict] = None
    circuit_group: Optional[dict] = None
    reported_by_user: Optional[dict] = None
    assigned_to_user: Optional[dict] = None
    resolved_by_user: Optional[dict] = None
    documents: List[dict] = Field(default_factory=list)
    
    class Config:
        from_attributes = True
