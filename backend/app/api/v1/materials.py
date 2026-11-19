"""
Materialkatalog-API
CRUD-Operationen für Materialkatalog und Leuchtmittel
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from typing import Optional
import logging

from app.database import get_db
from app.models.material import MaterialCatalog, Lamp
from app.schemas.material import (
    MaterialCatalogCreate, MaterialCatalogUpdate, MaterialCatalogResponse,
    LampCreate, LampUpdate, LampResponse
)
from app.schemas.common import PaginatedResponse, MessageResponse
from app.utils.security import get_current_active_user, require_admin
from app.utils.exceptions import NotFoundException, DuplicateEntryException
from app.utils.pagination import paginate, PaginationParams

router = APIRouter()
logger = logging.getLogger("sailight.materials")


# =============================================================================
# Materialkatalog-Endpoints
# =============================================================================

@router.get("/catalog", response_model=PaginatedResponse[MaterialCatalogResponse], summary="Alle Materialien abrufen")
async def read_materials(
    pagination: PaginationParams = Depends(),
    search: Optional[str] = Query(default=None, description="Suchbegriff"),
    category: Optional[str] = Query(default=None, description="Filter nach Kategorie"),
    manufacturer: Optional[str] = Query(default=None, description="Filter nach Hersteller"),
    is_active: Optional[bool] = Query(default=None, description="Filter nach Aktivitätsstatus"),
    db: AsyncSession = Depends(get_db),
    current_user: None = Depends(get_current_active_user)
):
    """Ruft alle Materialien aus dem Katalog ab"""
    query = select(MaterialCatalog).options(
        selectinload(MaterialCatalog.lamps),
        selectinload(MaterialCatalog.light_point_materials),
        selectinload(MaterialCatalog.cabinet_materials)
    )
    
    if search:
        query = query.where(
            MaterialCatalog.name.ilike(f"%{search}%") |
            MaterialCatalog.description.ilike(f"%{search}%")
        )
    
    if category:
        query = query.where(MaterialCatalog.category == category)
    
    if manufacturer:
        query = query.where(MaterialCatalog.manufacturer.ilike(f"%{manufacturer}%"))
    
    if is_active is not None:
        query = query.where(MaterialCatalog.is_active == is_active)
    
    query = query.order_by(MaterialCatalog.category, MaterialCatalog.name)
    return await paginate(db, query, pagination, MaterialCatalogResponse)


@router.post("/catalog", response_model=MaterialCatalogResponse, status_code=status.HTTP_201_CREATED, summary="Material erstellen")
async def create_material(
    material: MaterialCatalogCreate,
    db: AsyncSession = Depends(get_db),
    current_user: None = Depends(require_admin)
):
    """Erstellt ein neues Material im Katalog"""
    new_material = MaterialCatalog(**material.model_dump())
    db.add(new_material)
    await db.commit()
    await db.refresh(new_material)
    
    logger.info(f"Material '{material.name}' erstellt")
    return new_material


@router.get("/catalog/{material_id}", response_model=MaterialCatalogResponse, summary="Material abrufen")
async def read_material(
    material_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: None = Depends(get_current_active_user)
):
    """Ruft ein bestimmtes Material ab"""
    result = await db.execute(
        select(MaterialCatalog).where(MaterialCatalog.id == material_id)
        .options(
            selectinload(MaterialCatalog.lamps),
            selectinload(MaterialCatalog.light_point_materials),
            selectinload(MaterialCatalog.cabinet_materials)
        )
    )
    material = result.scalar_one_or_none()
    
    if not material:
        raise NotFoundException("Material", material_id)
    
    return material


@router.put("/catalog/{material_id}", response_model=MaterialCatalogResponse, summary="Material aktualisieren")
async def update_material(
    material_id: int,
    material: MaterialCatalogUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: None = Depends(require_admin)
):
    """Aktualisiert ein Material"""
    result = await db.execute(
        select(MaterialCatalog).where(MaterialCatalog.id == material_id)
    )
    existing_material = result.scalar_one_or_none()
    
    if not existing_material:
        raise NotFoundException("Material", material_id)
    
    for key, value in material.model_dump(exclude_unset=True).items():
        setattr(existing_material, key, value)
    
    await db.commit()
    await db.refresh(existing_material)
    
    logger.info(f"Material {material_id} aktualisiert")
    return existing_material


@router.delete("/catalog/{material_id}", response_model=MessageResponse, summary="Material löschen")
async def delete_material(
    material_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: None = Depends(require_admin)
):
    """Löscht ein Material"""
    result = await db.execute(
        select(MaterialCatalog).where(MaterialCatalog.id == material_id)
    )
    material = result.scalar_one_or_none()
    
    if not material:
        raise NotFoundException("Material", material_id)
    
    await db.delete(material)
    await db.commit()
    
    logger.info(f"Material {material_id} gelöscht")
    return MessageResponse(message=f"Material '{material.name}' wurde gelöscht")


# =============================================================================
# Leuchtmittel-Endpoints
# =============================================================================

@router.get("/lamps", response_model=PaginatedResponse[LampResponse], summary="Alle Leuchtmittel abrufen")
async def read_lamps(
    pagination: PaginationParams = Depends(),
    search: Optional[str] = Query(default=None, description="Suchbegriff"),
    material_id: Optional[int] = Query(default=None, description="Filter nach Material"),
    type: Optional[str] = Query(default=None, description="Filter nach Typ"),
    status: Optional[str] = Query(default=None, description="Filter nach Status"),
    db: AsyncSession = Depends(get_db),
    current_user: None = Depends(get_current_active_user)
):
    """Ruft alle Leuchtmittel ab"""
    query = select(Lamp).options(
        selectinload(Lamp.material),
        selectinload(Lamp.light_points)
    )
    
    if search:
        query = query.where(
            Lamp.identifier.ilike(f"%{search}%") |
            Lamp.type.ilike(f"%{search}%")
        )
    
    if material_id:
        query = query.where(Lamp.material_id == material_id)
    
    if type:
        query = query.where(Lamp.type == type)
    
    if status:
        query = query.where(Lamp.status == status)
    
    query = query.order_by(Lamp.type, Lamp.identifier)
    return await paginate(db, query, pagination, LampResponse)


@router.post("/lamps", response_model=LampResponse, status_code=status.HTTP_201_CREATED, summary="Leuchtmittel erstellen")
async def create_lamp(
    lamp: LampCreate,
    db: AsyncSession = Depends(get_db),
    current_user: None = Depends(require_admin)
):
    """Erstellt ein neues Leuchtmittel"""
    result = await db.execute(
        select(Lamp).where(Lamp.identifier == lamp.identifier)
    )
    existing = result.scalar_one_or_none()
    
    if existing:
        raise DuplicateEntryException("Leuchtmittel-Identifier", lamp.identifier)
    
    new_lamp = Lamp(**lamp.model_dump())
    db.add(new_lamp)
    await db.commit()
    await db.refresh(new_lamp)
    
    logger.info(f"Leuchtmittel '{lamp.identifier}' erstellt")
    return new_lamp


@router.get("/lamps/{lamp_id}", response_model=LampResponse, summary="Leuchtmittel abrufen")
async def read_lamp(
    lamp_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: None = Depends(get_current_active_user)
):
    """Ruft ein bestimmtes Leuchtmittel ab"""
    result = await db.execute(
        select(Lamp).where(Lamp.id == lamp_id)
        .options(
            selectinload(Lamp.material),
            selectinload(Lamp.light_points)
        )
    )
    lamp = result.scalar_one_or_none()
    
    if not lamp:
        raise NotFoundException("Leuchtmittel", lamp_id)
    
    return lamp


@router.put("/lamps/{lamp_id}", response_model=LampResponse, summary="Leuchtmittel aktualisieren")
async def update_lamp(
    lamp_id: int,
    lamp: LampUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: None = Depends(require_admin)
):
    """Aktualisiert ein Leuchtmittel"""
    result = await db.execute(
        select(Lamp).where(Lamp.id == lamp_id)
    )
    existing_lamp = result.scalar_one_or_none()
    
    if not existing_lamp:
        raise NotFoundException("Leuchtmittel", lamp_id)
    
    if lamp.identifier and lamp.identifier != existing_lamp.identifier:
        result = await db.execute(
            select(Lamp).where(Lamp.identifier == lamp.identifier, Lamp.id != lamp_id)
        )
        existing = result.scalar_one_or_none()
        
        if existing:
            raise DuplicateEntryException("Leuchtmittel-Identifier", lamp.identifier)
    
    for key, value in lamp.model_dump(exclude_unset=True).items():
        setattr(existing_lamp, key, value)
    
    await db.commit()
    await db.refresh(existing_lamp)
    
    logger.info(f"Leuchtmittel {lamp_id} aktualisiert")
    return existing_lamp


@router.delete("/lamps/{lamp_id}", response_model=MessageResponse, summary="Leuchtmittel löschen")
async def delete_lamp(
    lamp_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: None = Depends(require_admin)
):
    """Löscht ein Leuchtmittel"""
    result = await db.execute(
        select(Lamp).where(Lamp.id == lamp_id)
    )
    lamp = result.scalar_one_or_none()
    
    if not lamp:
        raise NotFoundException("Leuchtmittel", lamp_id)
    
    await db.delete(lamp)
    await db.commit()
    
    logger.info(f"Leuchtmittel {lamp_id} gelöscht")
    return MessageResponse(message=f"Leuchtmittel '{lamp.identifier}' wurde gelöscht")
