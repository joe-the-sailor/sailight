"""
Schaltschrank-API
CRUD-Operationen für Schaltschränke
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy import and_, or_
from typing import List, Optional
import logging

from app.database import get_db
from app.models.infrastructure import Cabinet
from app.models.geography import Street
from app.schemas.infrastructure import CabinetCreate, CabinetUpdate, CabinetResponse
from app.schemas.common import PaginatedResponse, MessageResponse
from app.utils.security import get_current_active_user, require_admin
from app.utils.exceptions import NotFoundException, DuplicateEntryException
from app.utils.pagination import paginate, PaginationParams
from app.utils.gis import validate_geometry

router = APIRouter()
logger = logging.getLogger("sailight.cabinets")


@router.get("/", response_model=PaginatedResponse[CabinetResponse], summary="Alle Schaltschränke abrufen")
async def read_cabinets(
    pagination: PaginationParams = Depends(),
    search: Optional[str] = Query(default=None, description="Suchbegriff"),
    street_id: Optional[int] = Query(default=None, description="Filter nach Straße"),
    status: Optional[str] = Query(default=None, description="Filter nach Status"),
    responsible_user_id: Optional[int] = Query(default=None, description="Filter nach verantwortlichem Benutzer"),
    db: AsyncSession = Depends(get_db),
    current_user: None = Depends(get_current_active_user)
):
    """Ruft alle Schaltschränke ab"""
    query = select(Cabinet).options(
        selectinload(Cabinet.street)
        .selectinload(Street.municipality)
        .selectinload(Cabinet.responsible_user)
    )
    
    # Filter anwenden
    if search:
        query = query.where(
            or_(
                Cabinet.name.ilike(f"%{search}%"),
                Cabinet.identifier.ilike(f"%{search}%")
            )
        )
    
    if street_id:
        query = query.where(Cabinet.street_id == street_id)
    
    if status:
        query = query.where(Cabinet.status == status)
    
    if responsible_user_id:
        query = query.where(Cabinet.responsible_user_id == responsible_user_id)
    
    query = query.order_by(Cabinet.identifier)
    return await paginate(db, query, pagination, CabinetResponse)


@router.post("/", response_model=CabinetResponse, status_code=status.HTTP_201_CREATED, summary="Schaltschrank erstellen")
async def create_cabinet(
    cabinet: CabinetCreate,
    db: AsyncSession = Depends(get_db),
    current_user: None = Depends(require_admin)
):
    """Erstellt einen neuen Schaltschrank"""
    # Prüfen, ob Identifier bereits existiert
    result = await db.execute(
        select(Cabinet).where(Cabinet.identifier == cabinet.identifier)
    )
    existing = result.scalar_one_or_none()
    
    if existing:
        raise DuplicateEntryException("Schaltschrank-Identifier", cabinet.identifier)
    
    # Geometrie validieren (falls vorhanden)
    if cabinet.geom:
        validate_geometry(cabinet.geom)
    
    new_cabinet = Cabinet(**cabinet.model_dump())
    db.add(new_cabinet)
    await db.commit()
    await db.refresh(new_cabinet)
    
    logger.info(f"Schaltschrank '{cabinet.identifier}' erstellt")
    return new_cabinet


@router.get("/{cabinet_id}", response_model=CabinetResponse, summary="Schaltschrank abrufen")
async def read_cabinet(
    cabinet_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: None = Depends(get_current_active_user)
):
    """Ruft einen bestimmten Schaltschrank ab"""
    result = await db.execute(
        select(Cabinet).where(Cabinet.id == cabinet_id)
        .options(
            selectinload(Cabinet.street)
            .selectinload(Street.municipality)
            .selectinload(Cabinet.responsible_user),
            selectinload(Cabinet.circuit_groups),
            selectinload(Cabinet.electric_meters)
        )
    )
    cabinet = result.scalar_one_or_none()
    
    if not cabinet:
        raise NotFoundException("Schaltschrank", cabinet_id)
    
    return cabinet


@router.put("/{cabinet_id}", response_model=CabinetResponse, summary="Schaltschrank aktualisieren")
async def update_cabinet(
    cabinet_id: int,
    cabinet: CabinetUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: None = Depends(require_admin)
):
    """Aktualisiert einen Schaltschrank"""
    result = await db.execute(
        select(Cabinet).where(Cabinet.id == cabinet_id)
    )
    existing_cabinet = result.scalar_one_or_none()
    
    if not existing_cabinet:
        raise NotFoundException("Schaltschrank", cabinet_id)
    
    # Prüfen, ob Identifier bereits existiert (wenn geändert)
    if cabinet.identifier and cabinet.identifier != existing_cabinet.identifier:
        result = await db.execute(
            select(Cabinet).where(Cabinet.identifier == cabinet.identifier, Cabinet.id != cabinet_id)
        )
        existing = result.scalar_one_or_none()
        
        if existing:
            raise DuplicateEntryException("Schaltschrank-Identifier", cabinet.identifier)
    
    # Geometrie validieren (falls vorhanden)
    if cabinet.geom:
        validate_geometry(cabinet.geom)
    
    # Aktualisieren
    for key, value in cabinet.model_dump(exclude_unset=True).items():
        setattr(existing_cabinet, key, value)
    
    await db.commit()
    await db.refresh(existing_cabinet)
    
    logger.info(f"Schaltschrank {cabinet_id} aktualisiert")
    return existing_cabinet


@router.delete("/{cabinet_id}", response_model=MessageResponse, summary="Schaltschrank löschen")
async def delete_cabinet(
    cabinet_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: None = Depends(require_admin)
):
    """Löscht einen Schaltschrank"""
    result = await db.execute(
        select(Cabinet).where(Cabinet.id == cabinet_id)
    )
    cabinet = result.scalar_one_or_none()
    
    if not cabinet:
        raise NotFoundException("Schaltschrank", cabinet_id)
    
    await db.delete(cabinet)
    await db.commit()
    
    logger.info(f"Schaltschrank {cabinet_id} gelöscht")
    return MessageResponse(message=f"Schaltschrank '{cabinet.identifier}' wurde gelöscht")


@router.get("/{cabinet_id}/statistics", summary="Statistiken für Schaltschrank abrufen")
async def get_cabinet_statistics(
    cabinet_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: None = Depends(get_current_active_user)
):
    """Ruft Statistiken für einen Schaltschrank ab"""
    result = await db.execute(
        select(Cabinet).where(Cabinet.id == cabinet_id)
        .options(
            selectinload(Cabinet.circuit_groups)
            .selectinload(Cabinet.electric_meters)
        )
    )
    cabinet = result.scalar_one_or_none()
    
    if not cabinet:
        raise NotFoundException("Schaltschrank", cabinet_id)
    
    # Statistiken berechnen
    circuit_group_count = len(cabinet.circuit_groups) if cabinet.circuit_groups else 0
    light_point_count = 0
    for cg in cabinet.circuit_groups:
        light_point_count += len(cg.light_points) if cg.light_points else 0
    
    meter_count = len(cabinet.electric_meters) if cabinet.electric_meters else 0
    
    return {
        "cabinet_id": cabinet.id,
        "identifier": cabinet.identifier,
        "name": cabinet.name,
        "circuit_group_count": circuit_group_count,
        "light_point_count": light_point_count,
        "meter_count": meter_count,
        "status": cabinet.status
    }
