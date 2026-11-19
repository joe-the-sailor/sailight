"""
Leuchtstellen-API
CRUD-Operationen für Leuchtstellen (POIs)
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy import and_, or_
from typing import Optional, List
import logging

from app.database import get_db
from app.models.infrastructure import LightPoint
from app.models.geography import Street
from app.schemas.infrastructure import LightPointCreate, LightPointUpdate, LightPointResponse
from app.schemas.common import PaginatedResponse, MessageResponse, BoundingBox, GISFilterParams
from app.utils.security import get_current_active_user, require_admin
from app.utils.exceptions import NotFoundException, DuplicateEntryException
from app.utils.pagination import paginate, PaginationParams
from app.utils.gis import validate_geometry

router = APIRouter()
logger = logging.getLogger("sailight.light_points")


@router.get("/", response_model=PaginatedResponse[LightPointResponse], summary="Alle Leuchtstellen abrufen")
async def read_light_points(
    pagination: PaginationParams = Depends(),
    search: Optional[str] = Query(default=None, description="Suchbegriff"),
    circuit_group_id: Optional[int] = Query(default=None, description="Filter nach Leitungsgruppe"),
    pole_id: Optional[int] = Query(default=None, description="Filter nach Mast"),
    status: Optional[str] = Query(default=None, description="Filter nach Status"),
    street_id: Optional[int] = Query(default=None, description="Filter nach Straße"),
    municipality_id: Optional[int] = Query(default=None, description="Filter nach Gemeinde"),
    db: AsyncSession = Depends(get_db),
    current_user: None = Depends(get_current_active_user)
):
    """Ruft alle Leuchtstellen ab"""
    query = select(LightPoint).options(
        selectinload(LightPoint.circuit_group)
        .selectinload(LightPoint.pole)
        .selectinload(LightPoint.lamp)
    )
    
    # Filter anwenden
    if search:
        query = query.where(
            or_(
                LightPoint.identifier.ilike(f"%{search}%"),
                LightPoint.light_type.ilike(f"%{search}%")
            )
        )
    
    if circuit_group_id:
        query = query.where(LightPoint.circuit_group_id == circuit_group_id)
    
    if pole_id:
        query = query.where(LightPoint.pole_id == pole_id)
    
    if status:
        query = query.where(LightPoint.status == status)
    
    query = query.order_by(LightPoint.identifier)
    return await paginate(db, query, pagination, LightPointResponse)


@router.get("/gis", summary="Leuchtstellen im GIS-Bereich abrufen")
async def read_light_points_gis(
    bbox: Optional[BoundingBox] = Query(default=None, description="Bounding Box"),
    radius: Optional[float] = Query(default=None, description="Radius in Metern"),
    center_lon: Optional[float] = Query(default=None, description="Zentrum Länge"),
    center_lat: Optional[float] = Query(default=None, description="Zentrum Breite"),
    db: AsyncSession = Depends(get_db),
    current_user: None = Depends(get_current_active_user)
):
    """Ruft Leuchtstellen im GIS-Bereich ab"""
    from geoalchemy2 import functions
    
    query = select(LightPoint).options(
        selectinload(LightPoint.circuit_group)
        .selectinload(LightPoint.pole)
    )
    
    if bbox:
        # Filter nach Bounding Box
        query = query.where(
            functions.ST_Within(
                LightPoint.geom,
                functions.ST_MakeEnvelope(
                    bbox.min_lon, bbox.min_lat,
                    bbox.max_lon, bbox.max_lat,
                    4326
                )
            )
        )
    
    if radius and center_lon and center_lat:
        # Filter nach Radius
        center_point = functions.ST_SetSRID(
            functions.ST_MakePoint(center_lon, center_lat),
            4326
        )
        query = query.where(
            functions.ST_DWithin(
                LightPoint.geom,
                center_point,
                radius
            )
        )
    
    result = await db.execute(query.limit(1000))
    light_points = result.scalars().all()
    
    features = []
    for lp in light_points:
        features.append({
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [lp.geom.x, lp.geom.y] if lp.geom else [0, 0]
            },
            "properties": {
                "id": lp.id,
                "identifier": lp.identifier,
                "status": lp.status,
                "light_type": lp.light_type,
                "power": lp.power,
                "circuit_group_id": lp.circuit_group_id,
                "pole_id": lp.pole_id
            }
        })
    
    return {
        "type": "FeatureCollection",
        "features": features
    }


@router.post("/", response_model=LightPointResponse, status_code=status.HTTP_201_CREATED, summary="Leuchtstelle erstellen")
async def create_light_point(
    light_point: LightPointCreate,
    db: AsyncSession = Depends(get_db),
    current_user: None = Depends(require_admin)
):
    """Erstellt eine neue Leuchtstelle"""
    result = await db.execute(
        select(LightPoint).where(LightPoint.identifier == light_point.identifier)
    )
    existing = result.scalar_one_or_none()
    
    if existing:
        raise DuplicateEntryException("Leuchtstellen-Identifier", light_point.identifier)
    
    if light_point.geom:
        validate_geometry(light_point.geom)
    
    new_light_point = LightPoint(**light_point.model_dump())
    db.add(new_light_point)
    await db.commit()
    await db.refresh(new_light_point)
    
    logger.info(f"Leuchtstelle '{light_point.identifier}' erstellt")
    return new_light_point


@router.get("/{light_point_id}", response_model=LightPointResponse, summary="Leuchtstelle abrufen")
async def read_light_point(
    light_point_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: None = Depends(get_current_active_user)
):
    """Ruft eine bestimmte Leuchtstelle ab"""
    result = await db.execute(
        select(LightPoint).where(LightPoint.id == light_point_id)
        .options(
            selectinload(LightPoint.circuit_group)
            .selectinload(LightPoint.pole)
            .selectinload(LightPoint.lamp),
            selectinload(LightPoint.materials)
        )
    )
    light_point = result.scalar_one_or_none()
    
    if not light_point:
        raise NotFoundException("Leuchtstelle", light_point_id)
    
    return light_point


@router.put("/{light_point_id}", response_model=LightPointResponse, summary="Leuchtstelle aktualisieren")
async def update_light_point(
    light_point_id: int,
    light_point: LightPointUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: None = Depends(require_admin)
):
    """Aktualisiert eine Leuchtstelle"""
    result = await db.execute(
        select(LightPoint).where(LightPoint.id == light_point_id)
    )
    existing_light_point = result.scalar_one_or_none()
    
    if not existing_light_point:
        raise NotFoundException("Leuchtstelle", light_point_id)
    
    if light_point.identifier and light_point.identifier != existing_light_point.identifier:
        result = await db.execute(
            select(LightPoint).where(
                LightPoint.identifier == light_point.identifier,
                LightPoint.id != light_point_id
            )
        )
        existing = result.scalar_one_or_none()
        
        if existing:
            raise DuplicateEntryException("Leuchtstellen-Identifier", light_point.identifier)
    
    if light_point.geom:
        validate_geometry(light_point.geom)
    
    for key, value in light_point.model_dump(exclude_unset=True).items():
        setattr(existing_light_point, key, value)
    
    await db.commit()
    await db.refresh(existing_light_point)
    
    logger.info(f"Leuchtstelle {light_point_id} aktualisiert")
    return existing_light_point


@router.delete("/{light_point_id}", response_model=MessageResponse, summary="Leuchtstelle löschen")
async def delete_light_point(
    light_point_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: None = Depends(require_admin)
):
    """Löscht eine Leuchtstelle"""
    result = await db.execute(
        select(LightPoint).where(LightPoint.id == light_point_id)
    )
    light_point = result.scalar_one_or_none()
    
    if not light_point:
        raise NotFoundException("Leuchtstelle", light_point_id)
    
    await db.delete(light_point)
    await db.commit()
    
    logger.info(f"Leuchtstelle {light_point_id} gelöscht")
    return MessageResponse(message=f"Leuchtstelle '{light_point.identifier}' wurde gelöscht")


@router.get("/{light_point_id}/statistics", summary="Statistiken für Leuchtstelle abrufen")
async def get_light_point_statistics(
    light_point_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: None = Depends(get_current_active_user)
):
    """Ruft Statistiken für eine Leuchtstelle ab"""
    result = await db.execute(
        select(LightPoint).where(LightPoint.id == light_point_id)
        .options(
            selectinload(LightPoint.circuit_group)
            .selectinload(LightPoint.pole)
        )
    )
    light_point = result.scalar_one_or_none()
    
    if not light_point:
        raise NotFoundException("Leuchtstelle", light_point_id)
    
    return {
        "light_point_id": light_point.id,
        "identifier": light_point.identifier,
        "status": light_point.status,
        "power": light_point.power,
        "light_type": light_point.light_type,
        "installation_date": light_point.installation_date,
        "last_maintenance_date": light_point.last_maintenance_date,
        "next_maintenance_date": light_point.next_maintenance_date,
        "circuit_group_id": light_point.circuit_group_id,
        "pole_id": light_point.pole_id,
        "lamp_id": light_point.lamp_id,
        "location": {
            "latitude": light_point.geom.y if light_point.geom else None,
            "longitude": light_point.geom.x if light_point.geom else None
        }
    }
