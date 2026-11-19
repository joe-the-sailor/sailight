"""
Gemeinsame Schemas für Pagination, Filter und Sortierung
"""

from pydantic import BaseModel, Field
from typing import Generic, TypeVar, List, Optional, Any, Dict
from enum import Enum

T = TypeVar('T')


class MessageResponse(BaseModel):
    """Einfache Nachricht als Response"""
    message: str
    detail: Optional[str] = None
    success: bool = True


class PaginatedResponse(BaseModel, Generic[T]):
    """Paginierte Response mit Metadaten"""
    items: List[T]
    total: int
    page: int = 1
    page_size: int = 50
    total_pages: int = 1
    has_next: bool = False
    has_previous: bool = False


class FilterParams(BaseModel):
    """Filter-Parameter für Abfragen"""
    search: Optional[str] = Field(default=None, description="Suchbegriff")
    status: Optional[str] = Field(default=None, description="Status-Filter")
    municipality_id: Optional[int] = Field(default=None, description="Gemeinde-ID")
    street_id: Optional[int] = Field(default=None, description="Straßen-ID")
    cabinet_id: Optional[int] = Field(default=None, description="Schaltschrank-ID")
    circuit_group_id: Optional[int] = Field(default=None, description="Leitungsgruppen-ID")
    pole_id: Optional[int] = Field(default=None, description="Mast-ID")
    start_date: Optional[str] = Field(default=None, description="Startdatum (YYYY-MM-DD)")
    end_date: Optional[str] = Field(default=None, description="Enddatum (YYYY-MM-DD)")


class SortParams(BaseModel):
    """Sortier-Parameter"""
    sort_by: Optional[str] = Field(default=None, description="Feld zum Sortieren")
    sort_order: str = Field(default="asc", description="Sortierrichtung (asc/desc)")


class GeometryResponse(BaseModel):
    """Schema für Geometrie-Daten"""
    type: str
    coordinates: List[Any]


class BoundingBox(BaseModel):
    """Bounding Box für GIS-Abfragen"""
    min_lon: float = Field(..., description="Minimale Länge")
    min_lat: float = Field(..., description="Minimale Breite")
    max_lon: float = Field(..., description="Maximale Länge")
    max_lat: float = Field(..., description="Maximale Breite")


class GISFilterParams(FilterParams):
    """Erweiterte Filter für GIS-Abfragen"""
    bbox: Optional[BoundingBox] = Field(default=None, description="Bounding Box")
    radius: Optional[float] = Field(default=None, description="Radius in Metern")
    center_lon: Optional[float] = Field(default=None, description="Zentrum Länge")
    center_lat: Optional[float] = Field(default=None, description="Zentrum Breite")
