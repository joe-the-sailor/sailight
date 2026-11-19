"""
Pydantic-Schemas für Infrastruktur: Schaltschränke, Leitungsgruppen, Masten, Leuchtstellen
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date
from decimal import Decimal


class CabinetBase(BaseModel):
    """Basis-Schema für Schaltschränke"""
    name: str = Field(..., min_length=1, max_length=100, description="Name")
    identifier: str = Field(..., min_length=1, max_length=50, description="Einzigartiger Identifier")
    street_id: Optional[int] = Field(default=None, description="Straßen-ID")
    geom: Optional[dict] = Field(default=None, description="Geometrie (Point)")
    status: str = Field(default="active", description="Status")
    voltage_level: Optional[str] = Field(default=None, max_length=20, description="Spannungsebene")
    installation_date: Optional[date] = Field(default=None, description="Installationsdatum")
    responsible_user_id: Optional[int] = Field(default=None, description="Verantwortlicher Benutzer")
    notes: Optional[str] = Field(default=None, description="Notizen")


class CabinetCreate(CabinetBase):
    """Schema zum Erstellen eines Schaltschranks"""
    pass


class CabinetUpdate(BaseModel):
    """Schema zum Aktualisieren eines Schaltschranks"""
    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    identifier: Optional[str] = Field(default=None, min_length=1, max_length=50)
    street_id: Optional[int] = Field(default=None)
    geom: Optional[dict] = Field(default=None)
    status: Optional[str] = Field(default=None)
    voltage_level: Optional[str] = Field(default=None, max_length=20)
    installation_date: Optional[date] = Field(default=None)
    responsible_user_id: Optional[int] = Field(default=None)
    notes: Optional[str] = Field(default=None)


class CabinetResponse(CabinetBase):
    """Response-Schema für Schaltschränke"""
    id: int
    uuid: str
    circuit_group_count: int = 0
    light_point_count: int = 0
    meter_count: int = 0
    created_at: datetime
    updated_at: datetime
    street: Optional[dict] = None
    responsible_user: Optional[dict] = None
    circuit_groups: List[dict] = Field(default_factory=list)
    electric_meters: List[dict] = Field(default_factory=list)
    
    class Config:
        from_attributes = True


class CircuitGroupBase(BaseModel):
    """Basis-Schema für Leitungsgruppen"""
    cabinet_id: int = Field(..., description="Schaltschrank-ID")
    name: str = Field(..., min_length=1, max_length=100, description="Name")
    identifier: str = Field(..., min_length=1, max_length=50, description="Einzigartiger Identifier")
    phase: Optional[str] = Field(default=None, max_length=10, description="Phase")
    fuse_rating: Optional[int] = Field(default=None, description="Sicherungsstärke (A)")
    cable_type_id: Optional[int] = Field(default=None, description="Kabeltyp-ID")
    cable_length: Optional[Decimal] = Field(default=None, description="Kabellänge (m)")
    status: str = Field(default="active", description="Status")
    installation_date: Optional[date] = Field(default=None, description="Installationsdatum")
    notes: Optional[str] = Field(default=None, description="Notizen")


class CircuitGroupCreate(CircuitGroupBase):
    """Schema zum Erstellen einer Leitungsgruppe"""
    pass


class CircuitGroupUpdate(BaseModel):
    """Schema zum Aktualisieren einer Leitungsgruppe"""
    cabinet_id: Optional[int] = Field(default=None)
    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    identifier: Optional[str] = Field(default=None, min_length=1, max_length=50)
    phase: Optional[str] = Field(default=None, max_length=10)
    fuse_rating: Optional[int] = Field(default=None)
    cable_type_id: Optional[int] = Field(default=None)
    cable_length: Optional[Decimal] = Field(default=None)
    status: Optional[str] = Field(default=None)
    installation_date: Optional[date] = Field(default=None)
    notes: Optional[str] = Field(default=None)


class CircuitGroupResponse(CircuitGroupBase):
    """Response-Schema für Leitungsgruppen"""
    id: int
    uuid: str
    light_point_count: int = 0
    created_at: datetime
    updated_at: datetime
    cabinet: Optional[dict] = None
    cable_type: Optional[dict] = None
    light_points: List[dict] = Field(default_factory=list)
    
    class Config:
        from_attributes = True


class PoleBase(BaseModel):
    """Basis-Schema für Masten"""
    street_id: Optional[int] = Field(default=None, description="Straßen-ID")
    identifier: str = Field(..., min_length=1, max_length=50, description="Einzigartiger Identifier")
    geom: Optional[dict] = Field(default=None, description="Geometrie (Point)")
    height: Optional[Decimal] = Field(default=None, description="Höhe (m)")
    type_id: Optional[int] = Field(default=None, description="Typ-ID (Materialkatalog)")
    material: Optional[str] = Field(default=None, max_length=50, description="Material")
    installation_date: Optional[date] = Field(default=None, description="Installationsdatum")
    status: str = Field(default="active", description="Status")
    owner: Optional[str] = Field(default=None, max_length=100, description="Eigentümer")
    notes: Optional[str] = Field(default=None, description="Notizen")


class PoleCreate(PoleBase):
    """Schema zum Erstellen eines Masts"""
    pass


class PoleUpdate(BaseModel):
    """Schema zum Aktualisieren eines Masts"""
    street_id: Optional[int] = Field(default=None)
    identifier: Optional[str] = Field(default=None, min_length=1, max_length=50)
    geom: Optional[dict] = Field(default=None)
    height: Optional[Decimal] = Field(default=None)
    type_id: Optional[int] = Field(default=None)
    material: Optional[str] = Field(default=None, max_length=50)
    installation_date: Optional[date] = Field(default=None)
    status: Optional[str] = Field(default=None)
    owner: Optional[str] = Field(default=None, max_length=100)
    notes: Optional[str] = Field(default=None)


class PoleResponse(PoleBase):
    """Response-Schema für Masten"""
    id: int
    uuid: str
    light_point_count: int = 0
    created_at: datetime
    updated_at: datetime
    street: Optional[dict] = None
    type: Optional[dict] = None
    light_points: List[dict] = Field(default_factory=list)
    
    class Config:
        from_attributes = True


class LightPointBase(BaseModel):
    """Basis-Schema für Leuchtstellen"""
    circuit_group_id: Optional[int] = Field(default=None, description="Leitungsgruppen-ID")
    pole_id: Optional[int] = Field(default=None, description="Mast-ID")
    identifier: str = Field(..., min_length=1, max_length=50, description="Einzigartiger Identifier")
    geom: Optional[dict] = Field(default=None, description="Geometrie (Point)")
    status: str = Field(default="active", description="Status")
    lamp_id: Optional[int] = Field(default=None, description="Leuchtmittel-ID")
    lamp_count: int = Field(default=1, description="Anzahl Leuchten")
    mounting_height: Optional[Decimal] = Field(default=None, description="Montagehöhe (m)")
    orientation: Optional[str] = Field(default=None, max_length=20, description="Ausrichtung")
    light_type: Optional[str] = Field(default=None, max_length=50, description="Leuchtentyp")
    power: Optional[int] = Field(default=None, description="Leistung (W)")
    installation_date: Optional[date] = Field(default=None, description="Installationsdatum")
    last_maintenance_date: Optional[date] = Field(default=None, description="Letzte Wartung")
    next_maintenance_date: Optional[date] = Field(default=None, description="Nächste Wartung")
    notes: Optional[str] = Field(default=None, description="Notizen")


class LightPointCreate(LightPointBase):
    """Schema zum Erstellen einer Leuchtstelle"""
    pass


class LightPointUpdate(BaseModel):
    """Schema zum Aktualisieren einer Leuchtstelle"""
    circuit_group_id: Optional[int] = Field(default=None)
    pole_id: Optional[int] = Field(default=None)
    identifier: Optional[str] = Field(default=None, min_length=1, max_length=50)
    geom: Optional[dict] = Field(default=None)
    status: Optional[str] = Field(default=None)
    lamp_id: Optional[int] = Field(default=None)
    lamp_count: Optional[int] = Field(default=None)
    mounting_height: Optional[Decimal] = Field(default=None)
    orientation: Optional[str] = Field(default=None, max_length=20)
    light_type: Optional[str] = Field(default=None, max_length=50)
    power: Optional[int] = Field(default=None)
    installation_date: Optional[date] = Field(default=None)
    last_maintenance_date: Optional[date] = Field(default=None)
    next_maintenance_date: Optional[date] = Field(default=None)
    notes: Optional[str] = Field(default=None)


class LightPointResponse(LightPointBase):
    """Response-Schema für Leuchtstellen"""
    id: int
    uuid: str
    full_identifier: str = ""
    location_description: str = ""
    created_at: datetime
    updated_at: datetime
    circuit_group: Optional[dict] = None
    pole: Optional[dict] = None
    lamp: Optional[dict] = None
    materials: List[dict] = Field(default_factory=list)
    
    class Config:
        from_attributes = True
