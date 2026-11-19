"""
Pydantic-Schemas für Projekte
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date
from decimal import Decimal


class ProjectTypeBase(BaseModel):
    """Basis-Schema für Projekt-Typen"""
    name: str = Field(..., min_length=1, max_length=100, description="Name")
    description: Optional[str] = Field(default=None, description="Beschreibung")
    is_active: bool = Field(default=True, description="Ist aktiv?")


class ProjectTypeCreate(ProjectTypeBase):
    """Schema zum Erstellen eines Projekt-Typs"""
    pass


class ProjectTypeUpdate(BaseModel):
    """Schema zum Aktualisieren eines Projekt-Typs"""
    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    description: Optional[str] = Field(default=None)
    is_active: Optional[bool] = Field(default=None)


class ProjectTypeResponse(ProjectTypeBase):
    """Response-Schema für Projekt-Typen"""
    id: int
    uuid: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class ProjectStatusBase(BaseModel):
    """Basis-Schema für Projekt-Status"""
    name: str = Field(..., min_length=1, max_length=50, description="Name")
    description: Optional[str] = Field(default=None, description="Beschreibung")
    is_active: bool = Field(default=True, description="Ist aktiv?")


class ProjectStatusCreate(ProjectStatusBase):
    """Schema zum Erstellen eines Projekt-Status"""
    pass


class ProjectStatusUpdate(BaseModel):
    """Schema zum Aktualisieren eines Projekt-Status"""
    name: Optional[str] = Field(default=None, min_length=1, max_length=50)
    description: Optional[str] = Field(default=None)
    is_active: Optional[bool] = Field(default=None)


class ProjectStatusResponse(ProjectStatusBase):
    """Response-Schema für Projekt-Status"""
    id: int
    uuid: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class ProjectBase(BaseModel):
    """Basis-Schema für Projekte"""
    project_type_id: Optional[int] = Field(default=None, description="Projekt-Typ-ID")
    project_status_id: Optional[int] = Field(default=None, description="Projekt-Status-ID")
    name: str = Field(..., min_length=1, max_length=200, description="Name")
    description: Optional[str] = Field(default=None, description="Beschreibung")
    identifier: str = Field(..., min_length=1, max_length=50, description="Einzigartiger Identifier")
    start_date: Optional[date] = Field(default=None, description="Startdatum")
    end_date: Optional[date] = Field(default=None, description="Enddatum")
    budget: Optional[Decimal] = Field(default=None, description="Budget (€)")
    actual_cost: Optional[Decimal] = Field(default=None, description="Tatsächliche Kosten (€)")
    responsible_user_id: Optional[int] = Field(default=None, description="Verantwortlicher Benutzer")
    municipality_id: Optional[int] = Field(default=None, description="Gemeinde-ID")
    notes: Optional[str] = Field(default=None, description="Notizen")


class ProjectCreate(ProjectBase):
    """Schema zum Erstellen eines Projekts"""
    pass


class ProjectUpdate(BaseModel):
    """Schema zum Aktualisieren eines Projekts"""
    project_type_id: Optional[int] = Field(default=None)
    project_status_id: Optional[int] = Field(default=None)
    name: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = Field(default=None)
    identifier: Optional[str] = Field(default=None, min_length=1, max_length=50)
    start_date: Optional[date] = Field(default=None)
    end_date: Optional[date] = Field(default=None)
    budget: Optional[Decimal] = Field(default=None)
    actual_cost: Optional[Decimal] = Field(default=None)
    responsible_user_id: Optional[int] = Field(default=None)
    municipality_id: Optional[int] = Field(default=None)
    notes: Optional[str] = Field(default=None)


class ProjectResponse(ProjectBase):
    """Response-Schema für Projekte"""
    id: int
    uuid: str
    created_at: datetime
    updated_at: datetime
    is_active: bool = False
    is_completed: bool = False
    budget_utilization: float = 0.0
    project_type: Optional[dict] = None
    project_status: Optional[dict] = None
    responsible_user: Optional[dict] = None
    municipality: Optional[dict] = None
    project_infrastructures: List[dict] = Field(default_factory=list)
    documents: List[dict] = Field(default_factory=list)
    
    class Config:
        from_attributes = True


class ProjectInfrastructureBase(BaseModel):
    """Basis-Schema für Projekt-Infrastruktur"""
    cabinet_id: Optional[int] = Field(default=None, description="Schaltschrank-ID")
    circuit_group_id: Optional[int] = Field(default=None, description="Leitungsgruppen-ID")
    pole_id: Optional[int] = Field(default=None, description="Mast-ID")
    light_point_id: Optional[int] = Field(default=None, description="Leuchtstellen-ID")
    incident_id: Optional[int] = Field(default=None, description="Störungs-ID")
    action: str = Field(..., min_length=1, max_length=50, description="Aktion")
    status: str = Field(default="planned", description="Status")
    notes: Optional[str] = Field(default=None, description="Notizen")


class ProjectInfrastructureCreate(ProjectInfrastructureBase):
    """Schema zum Erstellen einer Projekt-Infrastruktur-Verknüpfung"""
    pass


class ProjectInfrastructureUpdate(BaseModel):
    """Schema zum Aktualisieren einer Projekt-Infrastruktur-Verknüpfung"""
    cabinet_id: Optional[int] = Field(default=None)
    circuit_group_id: Optional[int] = Field(default=None)
    pole_id: Optional[int] = Field(default=None)
    light_point_id: Optional[int] = Field(default=None)
    incident_id: Optional[int] = Field(default=None)
    action: Optional[str] = Field(default=None, min_length=1, max_length=50)
    status: Optional[str] = Field(default=None)
    notes: Optional[str] = Field(default=None)


class ProjectInfrastructureResponse(ProjectInfrastructureBase):
    """Response-Schema für Projekt-Infrastruktur-Verknüpfungen"""
    id: int
    project_id: int
    created_at: datetime
    cabinet: Optional[dict] = None
    circuit_group: Optional[dict] = None
    pole: Optional[dict] = None
    light_point: Optional[dict] = None
    incident: Optional[dict] = None
    
    class Config:
        from_attributes = True
