"""
Pydantic-Schemas für Materialwirtschaft
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date
from decimal import Decimal


class MaterialCatalogBase(BaseModel):
    """Basis-Schema für Materialkatalog"""
    category: str = Field(..., min_length=1, max_length=50, description="Kategorie")
    name: str = Field(..., min_length=1, max_length=200, description="Name")
    description: Optional[str] = Field(default=None, description="Beschreibung")
    manufacturer: Optional[str] = Field(default=None, max_length=100, description="Hersteller")
    unit: Optional[str] = Field(default=None, max_length=20, description="Einheit")
    unit_price: Optional[Decimal] = Field(default=None, description="Preis pro Einheit")
    lifespan: Optional[int] = Field(default=None, description="Lebensdauer in Jahren")
    is_active: bool = Field(default=True, description="Ist aktiv?")


class MaterialCatalogCreate(MaterialCatalogBase):
    """Schema zum Erstellen eines Materials"""
    pass


class MaterialCatalogUpdate(BaseModel):
    """Schema zum Aktualisieren eines Materials"""
    category: Optional[str] = Field(default=None, min_length=1, max_length=50)
    name: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = Field(default=None)
    manufacturer: Optional[str] = Field(default=None, max_length=100)
    unit: Optional[str] = Field(default=None, max_length=20)
    unit_price: Optional[Decimal] = Field(default=None)
    lifespan: Optional[int] = Field(default=None)
    is_active: Optional[bool] = Field(default=None)


class MaterialCatalogResponse(MaterialCatalogBase):
    """Response-Schema für Materialien"""
    id: int
    uuid: str
    lamp_count: int = 0
    created_at: datetime
    updated_at: datetime
    lamps: List[dict] = Field(default_factory=list)
    
    class Config:
        from_attributes = True


class LampBase(BaseModel):
    """Basis-Schema für Leuchtmittel"""
    material_id: Optional[int] = Field(default=None, description="Material-ID")
    identifier: str = Field(..., min_length=1, max_length=50, description="Einzigartiger Identifier")
    type: str = Field(..., min_length=1, max_length=50, description="Typ")
    color_temperature: Optional[int] = Field(default=None, description="Farbtemperatur in Kelvin")
    luminous_flux: Optional[int] = Field(default=None, description="Lichtstrom in Lumen")
    wattage: Optional[int] = Field(default=None, description="Leistung in Watt")
    purchase_date: Optional[date] = Field(default=None, description="Kaufdatum")
    warranty_expiry: Optional[date] = Field(default=None, description="Garantieende")
    status: str = Field(default="new", description="Status")
    notes: Optional[str] = Field(default=None, description="Notizen")


class LampCreate(LampBase):
    """Schema zum Erstellen eines Leuchtmittels"""
    pass


class LampUpdate(BaseModel):
    """Schema zum Aktualisieren eines Leuchtmittels"""
    material_id: Optional[int] = Field(default=None)
    identifier: Optional[str] = Field(default=None, min_length=1, max_length=50)
    type: Optional[str] = Field(default=None, min_length=1, max_length=50)
    color_temperature: Optional[int] = Field(default=None)
    luminous_flux: Optional[int] = Field(default=None)
    wattage: Optional[int] = Field(default=None)
    purchase_date: Optional[date] = Field(default=None)
    warranty_expiry: Optional[date] = Field(default=None)
    status: Optional[str] = Field(default=None)
    notes: Optional[str] = Field(default=None)


class LampResponse(LampBase):
    """Response-Schema für Leuchtmittel"""
    id: int
    uuid: str
    created_at: datetime
    updated_at: datetime
    material: Optional[dict] = None
    light_points: List[dict] = Field(default_factory=list)
    
    class Config:
        from_attributes = True
