"""
Pydantic-Schemas für Geografie: Länder, Regionen, Gemeinden, Straßen
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class CountryBase(BaseModel):
    """Basis-Schema für Länder"""
    name: str = Field(..., min_length=1, max_length=100, description="Name des Landes")
    iso_code: str = Field(..., min_length=2, max_length=2, description="ISO-Code (z.B. LU)")


class CountryCreate(CountryBase):
    """Schema zum Erstellen eines Landes"""
    pass


class CountryUpdate(BaseModel):
    """Schema zum Aktualisieren eines Landes"""
    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    iso_code: Optional[str] = Field(default=None, min_length=2, max_length=2)


class CountryResponse(CountryBase):
    """Response-Schema für Länder"""
    id: int
    uuid: str
    geom: Optional[dict] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class RegionBase(BaseModel):
    """Basis-Schema für Regionen"""
    country_id: int = Field(..., description="ID des Landes")
    name: str = Field(..., min_length=1, max_length=100, description="Name der Region")
    code: str = Field(..., min_length=1, max_length=10, description="Regionscode")


class RegionCreate(RegionBase):
    """Schema zum Erstellen einer Region"""
    pass


class RegionUpdate(BaseModel):
    """Schema zum Aktualisieren einer Region"""
    country_id: Optional[int] = Field(default=None)
    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    code: Optional[str] = Field(default=None, min_length=1, max_length=10)


class RegionResponse(RegionBase):
    """Response-Schema für Regionen"""
    id: int
    uuid: str
    geom: Optional[dict] = None
    created_at: datetime
    updated_at: datetime
    country: Optional[CountryResponse] = None
    
    class Config:
        from_attributes = True


class MunicipalityBase(BaseModel):
    """Basis-Schema für Gemeinden"""
    region_id: int = Field(..., description="ID der Region")
    name: str = Field(..., min_length=1, max_length=100, description="Name der Gemeinde")
    code: str = Field(..., min_length=1, max_length=10, description="Gemeindecode")


class MunicipalityCreate(MunicipalityBase):
    """Schema zum Erstellen einer Gemeinde"""
    pass


class MunicipalityUpdate(BaseModel):
    """Schema zum Aktualisieren einer Gemeinde"""
    region_id: Optional[int] = Field(default=None)
    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    code: Optional[str] = Field(default=None, min_length=1, max_length=10)


class MunicipalityResponse(MunicipalityBase):
    """Response-Schema für Gemeinden"""
    id: int
    uuid: str
    geom: Optional[dict] = None
    created_at: datetime
    updated_at: datetime
    region: Optional[RegionResponse] = None
    
    class Config:
        from_attributes = True


class StreetBase(BaseModel):
    """Basis-Schema für Straßen"""
    municipality_id: int = Field(..., description="ID der Gemeinde")
    name: str = Field(..., min_length=1, max_length=200, description="Name der Straße")
    street_number_start: Optional[int] = Field(default=None, description="Hausnummer von")
    street_number_end: Optional[int] = Field(default=None, description="Hausnummer bis")


class StreetCreate(StreetBase):
    """Schema zum Erstellen einer Straße"""
    pass


class StreetUpdate(BaseModel):
    """Schema zum Aktualisieren einer Straße"""
    municipality_id: Optional[int] = Field(default=None)
    name: Optional[str] = Field(default=None, min_length=1, max_length=200)
    street_number_start: Optional[int] = Field(default=None)
    street_number_end: Optional[int] = Field(default=None)


class StreetResponse(StreetBase):
    """Response-Schema für Straßen"""
    id: int
    uuid: str
    geom: Optional[dict] = None
    created_at: datetime
    updated_at: datetime
    municipality: Optional[MunicipalityResponse] = None
    
    class Config:
        from_attributes = True
