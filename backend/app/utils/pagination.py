"""
Pagination-Utilities für API-Endpoints
"""

from fastapi import Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func, select as sql_select
from typing import Type, TypeVar, Generic, Optional, List, Any
from pydantic import BaseModel
import math

T = TypeVar('T')


class PaginationParams(BaseModel):
    """Parameter für Pagination"""
    page: int = Query(default=1, ge=1, description="Seitenzahl")
    page_size: int = Query(default=50, ge=1, le=1000, description="Anzahl Elemente pro Seite")


async def paginate(
    db: AsyncSession,
    query,
    pagination: PaginationParams,
    response_model: Type[T]
) -> dict:
    """
    Führt eine paginierte Abfrage aus
    
    Args:
        db: Datenbank-Session
        query: SQLAlchemy-Abfrage
        pagination: Pagination-Parameter
        response_model: Pydantic-Response-Modell
    
    Returns:
        Dictionary mit paginierten Daten
    """
    # Gesamtanzahl der Elemente
    count_query = sql_select(func.count()).select_from(query.subquery())
    result = await db.execute(count_query)
    total = result.scalar()
    
    # Pagination berechnen
    offset = (pagination.page - 1) * pagination.page_size
    limit = pagination.page_size
    
    # Elemente abrufen
    query = query.offset(offset).limit(limit)
    result = await db.execute(query)
    items = result.scalars().all()
    
    # In Response-Modell konvertieren
    items_response = [response_model.model_validate(item, from_attributes=True) for item in items]
    
    # Metadaten
    total_pages = math.ceil(total / pagination.page_size) if total > 0 else 0
    has_next = pagination.page < total_pages
    has_previous = pagination.page > 1
    
    return {
        "items": items_response,
        "total": total,
        "page": pagination.page,
        "page_size": pagination.page_size,
        "total_pages": total_pages,
        "has_next": has_next,
        "has_previous": has_previous
    }


async def get_all(
    db: AsyncSession,
    query,
    response_model: Type[T]
) -> List[T]:
    """
    Führt eine Abfrage aus und gibt alle Ergebnisse zurück
    
    Args:
        db: Datenbank-Session
        query: SQLAlchemy-Abfrage
        response_model: Pydantic-Response-Modell
    
    Returns:
        Liste der Ergebnisse
    """
    result = await db.execute(query)
    items = result.scalars().all()
    return [response_model.model_validate(item, from_attributes=True) for item in items]


async def get_one(
    db: AsyncSession,
    query,
    response_model: Type[T],
    not_found_message: str = "Ressource nicht gefunden"
) -> T:
    """
    Führt eine Abfrage aus und gibt ein einzelnes Ergebnis zurück
    
    Args:
        db: Datenbank-Session
        query: SQLAlchemy-Abfrage
        response_model: Pydantic-Response-Modell
        not_found_message: Fehlermeldung wenn nicht gefunden
    
    Returns:
        Einzelnes Ergebnis
    
    Raises:
        NotFoundException: Wenn keine Ressource gefunden wurde
    """
    result = await db.execute(query)
    item = result.scalar_one_or_none()
    
    if not item:
        from app.utils.exceptions import NotFoundException
        raise NotFoundException(not_found_message)
    
    return response_model.model_validate(item, from_attributes=True)
