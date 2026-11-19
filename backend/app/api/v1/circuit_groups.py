"""
Leitungsgruppen-API
CRUD-Operationen für Leitungsgruppen
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from typing import Optional
import logging

from app.database import get_db
from app.models.infrastructure import CircuitGroup
from app.schemas.infrastructure import CircuitGroupCreate, CircuitGroupUpdate, CircuitGroupResponse
from app.schemas.common import PaginatedResponse, MessageResponse
from app.utils.security import get_current_active_user, require_admin
from app.utils.exceptions import NotFoundException, DuplicateEntryException
from app.utils.pagination import paginate, PaginationParams

router = APIRouter()
logger = logging.getLogger("sailight.circuit_groups")


@router.get("/", response_model=PaginatedResponse[CircuitGroupResponse], summary="Alle Leitungsgruppen abrufen")
async def read_circuit_groups(
    pagination: PaginationParams = Depends(),
    cabinet_id: Optional[int] = Query(default=None, description="Filter nach Schaltschrank"),
    search: Optional[str] = Query(default=None, description="Suchbegriff"),
    status: Optional[str] = Query(default=None, description="Filter nach Status"),
    db: AsyncSession = Depends(get_db),
    current_user: None = Depends(get_current_active_user)
):
    """Ruft alle Leitungsgruppen ab"""
    query = select(CircuitGroup).options(
        selectinload(CircuitGroup.cabinet),
        selectinload(CircuitGroup.cable_type),
        selectinload(CircuitGroup.light_points)
    )
    
    if cabinet_id:
        query = query.where(CircuitGroup.cabinet_id == cabinet_id)
    
    if search:
        query = query.where(
            CircuitGroup.name.ilike(f"%{search}%") |
            CircuitGroup.identifier.ilike(f"%{search}%")
        )
    
    if status:
        query = query.where(CircuitGroup.status == status)
    
    query = query.order_by(CircuitGroup.identifier)
    return await paginate(db, query, pagination, CircuitGroupResponse)


@router.post("/", response_model=CircuitGroupResponse, status_code=status.HTTP_201_CREATED, summary="Leitungsgruppe erstellen")
async def create_circuit_group(
    circuit_group: CircuitGroupCreate,
    db: AsyncSession = Depends(get_db),
    current_user: None = Depends(require_admin)
):
    """Erstellt eine neue Leitungsgruppe"""
    result = await db.execute(
        select(CircuitGroup).where(CircuitGroup.identifier == circuit_group.identifier)
    )
    existing = result.scalar_one_or_none()
    
    if existing:
        raise DuplicateEntryException("Leitungsgruppen-Identifier", circuit_group.identifier)
    
    new_circuit_group = CircuitGroup(**circuit_group.model_dump())
    db.add(new_circuit_group)
    await db.commit()
    await db.refresh(new_circuit_group)
    
    logger.info(f"Leitungsgruppe '{circuit_group.identifier}' erstellt")
    return new_circuit_group


@router.get("/{circuit_group_id}", response_model=CircuitGroupResponse, summary="Leitungsgruppe abrufen")
async def read_circuit_group(
    circuit_group_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: None = Depends(get_current_active_user)
):
    """Ruft eine bestimmte Leitungsgruppe ab"""
    result = await db.execute(
        select(CircuitGroup).where(CircuitGroup.id == circuit_group_id)
        .options(
            selectinload(CircuitGroup.cabinet),
            selectinload(CircuitGroup.cable_type),
            selectinload(CircuitGroup.light_points)
        )
    )
    circuit_group = result.scalar_one_or_none()
    
    if not circuit_group:
        raise NotFoundException("Leitungsgruppe", circuit_group_id)
    
    return circuit_group


@router.put("/{circuit_group_id}", response_model=CircuitGroupResponse, summary="Leitungsgruppe aktualisieren")
async def update_circuit_group(
    circuit_group_id: int,
    circuit_group: CircuitGroupUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: None = Depends(require_admin)
):
    """Aktualisiert eine Leitungsgruppe"""
    result = await db.execute(
        select(CircuitGroup).where(CircuitGroup.id == circuit_group_id)
    )
    existing_circuit_group = result.scalar_one_or_none()
    
    if not existing_circuit_group:
        raise NotFoundException("Leitungsgruppe", circuit_group_id)
    
    if circuit_group.identifier and circuit_group.identifier != existing_circuit_group.identifier:
        result = await db.execute(
            select(CircuitGroup).where(
                CircuitGroup.identifier == circuit_group.identifier,
                CircuitGroup.id != circuit_group_id
            )
        )
        existing = result.scalar_one_or_none()
        
        if existing:
            raise DuplicateEntryException("Leitungsgruppen-Identifier", circuit_group.identifier)
    
    for key, value in circuit_group.model_dump(exclude_unset=True).items():
        setattr(existing_circuit_group, key, value)
    
    await db.commit()
    await db.refresh(existing_circuit_group)
    
    logger.info(f"Leitungsgruppe {circuit_group_id} aktualisiert")
    return existing_circuit_group


@router.delete("/{circuit_group_id}", response_model=MessageResponse, summary="Leitungsgruppe löschen")
async def delete_circuit_group(
    circuit_group_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: None = Depends(require_admin)
):
    """Löscht eine Leitungsgruppe"""
    result = await db.execute(
        select(CircuitGroup).where(CircuitGroup.id == circuit_group_id)
    )
    circuit_group = result.scalar_one_or_none()
    
    if not circuit_group:
        raise NotFoundException("Leitungsgruppe", circuit_group_id)
    
    await db.delete(circuit_group)
    await db.commit()
    
    logger.info(f"Leitungsgruppe {circuit_group_id} gelöscht")
    return MessageResponse(message=f"Leitungsgruppe '{circuit_group.identifier}' wurde gelöscht")
