"""
Mast-API
CRUD-Operationen für Masten
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from typing import Optional
import logging

from app.database import get_db
from app.models.infrastructure import Pole
from app.models.geography import Street
from app.schemas.infrastructure import PoleCreate, PoleUpdate, PoleResponse
from app.schemas.common import PaginatedResponse, MessageResponse
from app.utils.security import get_current_active_user, require_admin
from app.utils.exceptions import NotFoundException, DuplicateEntryException
from app.utils.pagination import paginate, PaginationParams
from app.utils.gis import validate_geometry

router = APIRouter()
logger = logging.getLogger("sailight.poles")


@router.get("/", response_model=PaginatedResponse[PoleResponse], summary="Alle Masten abrufen")
async def read_poles(
    pagination: PaginationParams = Depends(),
    search: Optional[str] = Query(default=None, description="Suchbegriff"),
    street_id: Optional[int] = Query(default=None, description="Filter nach Straße"),
    status: Optional[str] = Query(default=None, description="Filter nach Status"),
    db: AsyncSession = Depends(get_db),
    current_user: None = Depends(get_current_active_user)
):
    """Ruft alle Masten ab"""
    query = select(Pole).options(
        selectinload(Pole.street)
        .selectinload(Street.municipality),
        selectinload(Pole.type),
        selectinload(Pole.light_points)
    )
    
    if search:
        query = query.where(
            Pole.identifier.ilike(f"%{search}%") |
            Pole.owner.ilike(f"%{search}%")
        )
    
    if street_id:
        query = query.where(Pole.street_id == street_id)
    
    if status:
        query = query.where(Pole.status == status)
    
    query = query.order_by(Pole.identifier)
    return await paginate(db, query, pagination, PoleResponse)


@router.post("/", response_model=PoleResponse, status_code=status.HTTP_201_CREATED, summary="Mast erstellen")
async def create_pole(
    pole: PoleCreate,
    db: AsyncSession = Depends(get_db),
    current_user: None = Depends(require_admin)
):
    """Erstellt einen neuen Mast"""
    result = await db.execute(
        select(Pole).where(Pole.identifier == pole.identifier)
    )
    existing = result.scalar_one_or_none()
    
    if existing:
        raise DuplicateEntryException("Mast-Identifier", pole.identifier)
    
    if pole.geom:
        validate_geometry(pole.geom)
    
    new_pole = Pole(**pole.model_dump())
    db.add(new_pole)
    await db.commit()
    await db.refresh(new_pole)
    
    logger.info(f"Mast '{pole.identifier}' erstellt")
    return new_pole


@router.get("/{pole_id}", response_model=PoleResponse, summary="Mast abrufen")
async def read_pole(
    pole_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: None = Depends(get_current_active_user)
):
    """Ruft einen bestimmten Mast ab"""
    result = await db.execute(
        select(Pole).where(Pole.id == pole_id)
        .options(
            selectinload(Pole.street)
            .selectinload(Street.municipality),
            selectinload(Pole.type),
            selectinload(Pole.light_points)
        )
    )
    pole = result.scalar_one_or_none()
    
    if not pole:
        raise NotFoundException("Mast", pole_id)
    
    return pole


@router.put("/{pole_id}", response_model=PoleResponse, summary="Mast aktualisieren")
async def update_pole(
    pole_id: int,
    pole: PoleUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: None = Depends(require_admin)
):
    """Aktualisiert einen Mast"""
    result = await db.execute(
        select(Pole).where(Pole.id == pole_id)
    )
    existing_pole = result.scalar_one_or_none()
    
    if not existing_pole:
        raise NotFoundException("Mast", pole_id)
    
    if pole.identifier and pole.identifier != existing_pole.identifier:
        result = await db.execute(
            select(Pole).where(Pole.identifier == pole.identifier, Pole.id != pole_id)
        )
        existing = result.scalar_one_or_none()
        
        if existing:
            raise DuplicateEntryException("Mast-Identifier", pole.identifier)
    
    if pole.geom:
        validate_geometry(pole.geom)
    
    for key, value in pole.model_dump(exclude_unset=True).items():
        setattr(existing_pole, key, value)
    
    await db.commit()
    await db.refresh(existing_pole)
    
    logger.info(f"Mast {pole_id} aktualisiert")
    return existing_pole


@router.delete("/{pole_id}", response_model=MessageResponse, summary="Mast löschen")
async def delete_pole(
    pole_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: None = Depends(require_admin)
):
    """Löscht einen Mast"""
    result = await db.execute(
        select(Pole).where(Pole.id == pole_id)
    )
    pole = result.scalar_one_or_none()
    
    if not pole:
        raise NotFoundException("Mast", pole_id)
    
    await db.delete(pole)
    await db.commit()
    
    logger.info(f"Mast {pole_id} gelöscht")
    return MessageResponse(message=f"Mast '{pole.identifier}' wurde gelöscht")
