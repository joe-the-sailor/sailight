"""
Geografie-API
CRUD-Operationen für Länder, Regionen, Gemeinden, Straßen
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from typing import List, Optional
import logging

from app.database import get_db
from app.models.geography import Country, Region, Municipality, Street
from app.schemas.geography import (
    CountryCreate, CountryUpdate, CountryResponse,
    RegionCreate, RegionUpdate, RegionResponse,
    MunicipalityCreate, MunicipalityUpdate, MunicipalityResponse,
    StreetCreate, StreetUpdate, StreetResponse
)
from app.schemas.common import PaginatedResponse, MessageResponse
from app.utils.security import get_current_active_user, require_admin
from app.utils.exceptions import NotFoundException, DuplicateEntryException
from app.utils.pagination import paginate, PaginationParams

router = APIRouter()
logger = logging.getLogger("sailight.geography")


# =============================================================================
# Länder-Endpoints
# =============================================================================

@router.get("/countries", response_model=PaginatedResponse[CountryResponse], summary="Alle Länder abrufen")
async def read_countries(
    pagination: PaginationParams = Depends(),
    db: AsyncSession = Depends(get_db),
    current_user: None = Depends(get_current_active_user)
):
    """Ruft alle Länder ab"""
    query = select(Country).order_by(Country.name)
    return await paginate(db, query, pagination, CountryResponse)


@router.post("/countries", response_model=CountryResponse, status_code=status.HTTP_201_CREATED, summary="Land erstellen")
async def create_country(
    country: CountryCreate,
    db: AsyncSession = Depends(get_db),
    current_user: None = Depends(require_admin)
):
    """Erstellt ein neues Land"""
    result = await db.execute(
        select(Country).where(Country.iso_code == country.iso_code)
    )
    existing = result.scalar_one_or_none()
    
    if existing:
        raise DuplicateEntryException("ISO-Code", country.iso_code)
    
    new_country = Country(**country.model_dump())
    db.add(new_country)
    await db.commit()
    await db.refresh(new_country)
    
    logger.info(f"Land '{country.name}' erstellt")
    return new_country


@router.get("/countries/{country_id}", response_model=CountryResponse, summary="Land abrufen")
async def read_country(
    country_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: None = Depends(get_current_active_user)
):
    """Ruft ein bestimmtes Land ab"""
    result = await db.execute(
        select(Country).where(Country.id == country_id)
    )
    country = result.scalar_one_or_none()
    
    if not country:
        raise NotFoundException("Land", country_id)
    
    return country


# =============================================================================
# Regionen-Endpoints
# =============================================================================

@router.get("/regions", response_model=PaginatedResponse[RegionResponse], summary="Alle Regionen abrufen")
async def read_regions(
    country_id: Optional[int] = Query(default=None, description="Filter nach Land"),
    pagination: PaginationParams = Depends(),
    db: AsyncSession = Depends(get_db),
    current_user: None = Depends(get_current_active_user)
):
    """Ruft alle Regionen ab"""
    query = select(Region).options(selectinload(Region.country))
    
    if country_id:
        query = query.where(Region.country_id == country_id)
    
    query = query.order_by(Region.name)
    return await paginate(db, query, pagination, RegionResponse)


@router.post("/regions", response_model=RegionResponse, status_code=status.HTTP_201_CREATED, summary="Region erstellen")
async def create_region(
    region: RegionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: None = Depends(require_admin)
):
    """Erstellt eine neue Region"""
    result = await db.execute(
        select(Region).where(Region.code == region.code)
    )
    existing = result.scalar_one_or_none()
    
    if existing:
        raise DuplicateEntryException("Regionscode", region.code)
    
    new_region = Region(**region.model_dump())
    db.add(new_region)
    await db.commit()
    await db.refresh(new_region)
    
    logger.info(f"Region '{region.name}' erstellt")
    return new_region


@router.get("/regions/{region_id}", response_model=RegionResponse, summary="Region abrufen")
async def read_region(
    region_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: None = Depends(get_current_active_user)
):
    """Ruft eine bestimmte Region ab"""
    result = await db.execute(
        select(Region).where(Region.id == region_id)
        .options(selectinload(Region.country))
    )
    region = result.scalar_one_or_none()
    
    if not region:
        raise NotFoundException("Region", region_id)
    
    return region


# =============================================================================
# Gemeinden-Endpoints
# =============================================================================

@router.get("/municipalities", response_model=PaginatedResponse[MunicipalityResponse], summary="Alle Gemeinden abrufen")
async def read_municipalities(
    region_id: Optional[int] = Query(default=None, description="Filter nach Region"),
    search: Optional[str] = Query(default=None, description="Suchbegriff"),
    pagination: PaginationParams = Depends(),
    db: AsyncSession = Depends(get_db),
    current_user: None = Depends(get_current_active_user)
):
    """Ruft alle Gemeinden ab"""
    query = select(Municipality).options(
        selectinload(Municipality.region)
        .selectinload(Region.country)
    )
    
    if region_id:
        query = query.where(Municipality.region_id == region_id)
    
    if search:
        query = query.where(
            Municipality.name.ilike(f"%{search}%") |
            Municipality.code.ilike(f"%{search}%")
        )
    
    query = query.order_by(Municipality.name)
    return await paginate(db, query, pagination, MunicipalityResponse)


@router.post("/municipalities", response_model=MunicipalityResponse, status_code=status.HTTP_201_CREATED, summary="Gemeinde erstellen")
async def create_municipality(
    municipality: MunicipalityCreate,
    db: AsyncSession = Depends(get_db),
    current_user: None = Depends(require_admin)
):
    """Erstellt eine neue Gemeinde"""
    result = await db.execute(
        select(Municipality).where(Municipality.code == municipality.code)
    )
    existing = result.scalar_one_or_none()
    
    if existing:
        raise DuplicateEntryException("Gemeindecode", municipality.code)
    
    new_municipality = Municipality(**municipality.model_dump())
    db.add(new_municipality)
    await db.commit()
    await db.refresh(new_municipality)
    
    logger.info(f"Gemeinde '{municipality.name}' erstellt")
    return new_municipality


@router.get("/municipalities/{municipality_id}", response_model=MunicipalityResponse, summary="Gemeinde abrufen")
async def read_municipality(
    municipality_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: None = Depends(get_current_active_user)
):
    """Ruft eine bestimmte Gemeinde ab"""
    result = await db.execute(
        select(Municipality).where(Municipality.id == municipality_id)
        .options(
            selectinload(Municipality.region)
            .selectinload(Region.country)
        )
    )
    municipality = result.scalar_one_or_none()
    
    if not municipality:
        raise NotFoundException("Gemeinde", municipality_id)
    
    return municipality


# =============================================================================
# Straßen-Endpoints
# =============================================================================

@router.get("/streets", response_model=PaginatedResponse[StreetResponse], summary="Alle Straßen abrufen")
async def read_streets(
    municipality_id: Optional[int] = Query(default=None, description="Filter nach Gemeinde"),
    search: Optional[str] = Query(default=None, description="Suchbegriff"),
    pagination: PaginationParams = Depends(),
    db: AsyncSession = Depends(get_db),
    current_user: None = Depends(get_current_active_user)
):
    """Ruft alle Straßen ab"""
    query = select(Street).options(
        selectinload(Street.municipality)
        .selectinload(Municipality.region)
        .selectinload(Region.country)
    )
    
    if municipality_id:
        query = query.where(Street.municipality_id == municipality_id)
    
    if search:
        query = query.where(
            Street.name.ilike(f"%{search}%")
        )
    
    query = query.order_by(Street.name)
    return await paginate(db, query, pagination, StreetResponse)


@router.post("/streets", response_model=StreetResponse, status_code=status.HTTP_201_CREATED, summary="Straße erstellen")
async def create_street(
    street: StreetCreate,
    db: AsyncSession = Depends(get_db),
    current_user: None = Depends(require_admin)
):
    """Erstellt eine neue Straße"""
    new_street = Street(**street.model_dump())
    db.add(new_street)
    await db.commit()
    await db.refresh(new_street)
    
    logger.info(f"Straße '{street.name}' erstellt")
    return new_street


@router.get("/streets/{street_id}", response_model=StreetResponse, summary="Straße abrufen")
async def read_street(
    street_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: None = Depends(get_current_active_user)
):
    """Ruft eine bestimmte Straße ab"""
    result = await db.execute(
        select(Street).where(Street.id == street_id)
        .options(
            selectinload(Street.municipality)
            .selectinload(Municipality.region)
            .selectinload(Region.country)
        )
    )
    street = result.scalar_one_or_none()
    
    if not street:
        raise NotFoundException("Straße", street_id)
    
    return street
