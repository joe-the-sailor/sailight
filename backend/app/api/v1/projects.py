"""
Projekt-API
CRUD-Operationen für Projekte
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from typing import Optional
import logging

from app.database import get_db
from app.models.project import Project, ProjectType, ProjectStatus, ProjectInfrastructure
from app.schemas.project import (
    ProjectTypeCreate, ProjectTypeUpdate, ProjectTypeResponse,
    ProjectStatusCreate, ProjectStatusUpdate, ProjectStatusResponse,
    ProjectCreate, ProjectUpdate, ProjectResponse,
    ProjectInfrastructureCreate, ProjectInfrastructureUpdate, ProjectInfrastructureResponse
)
from app.schemas.common import PaginatedResponse, MessageResponse
from app.utils.security import get_current_active_user, require_admin
from app.utils.exceptions import NotFoundException, DuplicateEntryException
from app.utils.pagination import paginate, PaginationParams

router = APIRouter()
logger = logging.getLogger("sailight.projects")


# =============================================================================
# Projekt-Typen-Endpoints
# =============================================================================

@router.get("/types", response_model=PaginatedResponse[ProjectTypeResponse], summary="Alle Projekt-Typen abrufen")
async def read_project_types(
    pagination: PaginationParams = Depends(),
    is_active: Optional[bool] = Query(default=None, description="Filter nach Aktivitätsstatus"),
    db: AsyncSession = Depends(get_db),
    current_user: None = Depends(get_current_active_user)
):
    """Ruft alle Projekt-Typen ab"""
    query = select(ProjectType)
    
    if is_active is not None:
        query = query.where(ProjectType.is_active == is_active)
    
    query = query.order_by(ProjectType.name)
    return await paginate(db, query, pagination, ProjectTypeResponse)


@router.post("/types", response_model=ProjectTypeResponse, status_code=status.HTTP_201_CREATED, summary="Projekt-Typ erstellen")
async def create_project_type(
    project_type: ProjectTypeCreate,
    db: AsyncSession = Depends(get_db),
    current_user: None = Depends(require_admin)
):
    """Erstellt einen neuen Projekt-Typ"""
    result = await db.execute(
        select(ProjectType).where(ProjectType.name == project_type.name)
    )
    existing = result.scalar_one_or_none()
    
    if existing:
        raise DuplicateEntryException("Projekt-Typ", project_type.name)
    
    new_type = ProjectType(**project_type.model_dump())
    db.add(new_type)
    await db.commit()
    await db.refresh(new_type)
    
    logger.info(f"Projekt-Typ '{project_type.name}' erstellt")
    return new_type


# =============================================================================
# Projekt-Status-Endpoints
# =============================================================================

@router.get("/statuses", response_model=PaginatedResponse[ProjectStatusResponse], summary="Alle Projekt-Status abrufen")
async def read_project_statuses(
    pagination: PaginationParams = Depends(),
    is_active: Optional[bool] = Query(default=None, description="Filter nach Aktivitätsstatus"),
    db: AsyncSession = Depends(get_db),
    current_user: None = Depends(get_current_active_user)
):
    """Ruft alle Projekt-Status ab"""
    query = select(ProjectStatus)
    
    if is_active is not None:
        query = query.where(ProjectStatus.is_active == is_active)
    
    query = query.order_by(ProjectStatus.name)
    return await paginate(db, query, pagination, ProjectStatusResponse)


# =============================================================================
# Projekt-Endpoints
# =============================================================================

@router.get("/", response_model=PaginatedResponse[ProjectResponse], summary="Alle Projekte abrufen")
async def read_projects(
    pagination: PaginationParams = Depends(),
    search: Optional[str] = Query(default=None, description="Suchbegriff"),
    project_type_id: Optional[int] = Query(default=None, description="Filter nach Projekt-Typ"),
    project_status_id: Optional[int] = Query(default=None, description="Filter nach Status"),
    responsible_user_id: Optional[int] = Query(default=None, description="Filter nach Verantwortlichem"),
    municipality_id: Optional[int] = Query(default=None, description="Filter nach Gemeinde"),
    is_active: Optional[bool] = Query(default=None, description="Filter nach aktiv/inaktiv"),
    start_date: Optional[str] = Query(default=None, description="Startdatum (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(default=None, description="Enddatum (YYYY-MM-DD)"),
    db: AsyncSession = Depends(get_db),
    current_user: None = Depends(get_current_active_user)
):
    """Ruft alle Projekte ab"""
    query = select(Project).options(
        selectinload(Project.project_type),
        selectinload(Project.project_status),
        selectinload(Project.responsible_user),
        selectinload(Project.municipality),
        selectinload(Project.project_infrastructures)
    )
    
    if search:
        query = query.where(
            Project.name.ilike(f"%{search}%") |
            Project.description.ilike(f"%{search}%") |
            Project.identifier.ilike(f"%{search}%")
        )
    
    if project_type_id:
        query = query.where(Project.project_type_id == project_type_id)
    
    if project_status_id:
        query = query.where(Project.project_status_id == project_status_id)
    
    if responsible_user_id:
        query = query.where(Project.responsible_user_id == responsible_user_id)
    
    if municipality_id:
        query = query.where(Project.municipality_id == municipality_id)
    
    if is_active is not None:
        query = query.where(Project.project_status.has(is_active=is_active))
    
    if start_date:
        query = query.where(Project.start_date >= start_date)
    
    if end_date:
        query = query.where(Project.end_date <= end_date)
    
    query = query.order_by(Project.start_date.desc())
    return await paginate(db, query, pagination, ProjectResponse)


@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED, summary="Projekt erstellen")
async def create_project(
    project: ProjectCreate,
    db: AsyncSession = Depends(get_db),
    current_user: None = Depends(require_admin)
):
    """Erstellt ein neues Projekt"""
    result = await db.execute(
        select(Project).where(Project.identifier == project.identifier)
    )
    existing = result.scalar_one_or_none()
    
    if existing:
        raise DuplicateEntryException("Projekt-Identifier", project.identifier)
    
    new_project = Project(**project.model_dump())
    db.add(new_project)
    await db.commit()
    await db.refresh(new_project)
    
    logger.info(f"Projekt '{project.identifier}' erstellt")
    return new_project


@router.get("/{project_id}", response_model=ProjectResponse, summary="Projekt abrufen")
async def read_project(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: None = Depends(get_current_active_user)
):
    """Ruft ein bestimmtes Projekt ab"""
    result = await db.execute(
        select(Project).where(Project.id == project_id)
        .options(
            selectinload(Project.project_type),
            selectinload(Project.project_status),
            selectinload(Project.responsible_user),
            selectinload(Project.municipality),
            selectinload(Project.project_infrastructures)
            .selectinload(ProjectInfrastructure.cabinet),
            selectinload(Project.project_infrastructures)
            .selectinload(ProjectInfrastructure.circuit_group),
            selectinload(Project.project_infrastructures)
            .selectinload(ProjectInfrastructure.pole),
            selectinload(Project.project_infrastructures)
            .selectinload(ProjectInfrastructure.light_point),
            selectinload(Project.documents)
        )
    )
    project = result.scalar_one_or_none()
    
    if not project:
        raise NotFoundException("Projekt", project_id)
    
    return project


@router.put("/{project_id}", response_model=ProjectResponse, summary="Projekt aktualisieren")
async def update_project(
    project_id: int,
    project: ProjectUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: None = Depends(require_admin)
):
    """Aktualisiert ein Projekt"""
    result = await db.execute(
        select(Project).where(Project.id == project_id)
    )
    existing_project = result.scalar_one_or_none()
    
    if not existing_project:
        raise NotFoundException("Projekt", project_id)
    
    if project.identifier and project.identifier != existing_project.identifier:
        result = await db.execute(
            select(Project).where(Project.identifier == project.identifier, Project.id != project_id)
        )
        existing = result.scalar_one_or_none()
        
        if existing:
            raise DuplicateEntryException("Projekt-Identifier", project.identifier)
    
    for key, value in project.model_dump(exclude_unset=True).items():
        setattr(existing_project, key, value)
    
    await db.commit()
    await db.refresh(existing_project)
    
    logger.info(f"Projekt {project_id} aktualisiert")
    return existing_project


# =============================================================================
# Projekt-Infrastruktur-Endpoints
# =============================================================================

@router.get("/{project_id}/infrastructure", response_model=PaginatedResponse[ProjectInfrastructureResponse], summary="Projekt-Infrastruktur abrufen")
async def read_project_infrastructure(
    project_id: int,
    pagination: PaginationParams = Depends(),
    db: AsyncSession = Depends(get_db),
    current_user: None = Depends(get_current_active_user)
):
    """Ruft die Infrastruktur-Elemente eines Projekts ab"""
    result = await db.execute(
        select(Project).where(Project.id == project_id)
    )
    project = result.scalar_one_or_none()
    
    if not project:
        raise NotFoundException("Projekt", project_id)
    
    query = select(ProjectInfrastructure).where(
        ProjectInfrastructure.project_id == project_id
    ).options(
        selectinload(ProjectInfrastructure.cabinet),
        selectinload(ProjectInfrastructure.circuit_group),
        selectinload(ProjectInfrastructure.pole),
        selectinload(ProjectInfrastructure.light_point)
    )
    
    query = query.order_by(ProjectInfrastructure.created_at)
    return await paginate(db, query, pagination, ProjectInfrastructureResponse)


@router.post("/{project_id}/infrastructure", response_model=ProjectInfrastructureResponse, status_code=status.HTTP_201_CREATED, summary="Infrastruktur-Element hinzufügen")
async def add_project_infrastructure(
    project_id: int,
    infrastructure: ProjectInfrastructureCreate,
    db: AsyncSession = Depends(get_db),
    current_user: None = Depends(require_admin)
):
    """Fügt ein Infrastruktur-Element zu einem Projekt hinzu"""
    result = await db.execute(
        select(Project).where(Project.id == project_id)
    )
    project = result.scalar_one_or_none()
    
    if not project:
        raise NotFoundException("Projekt", project_id)
    
    new_infrastructure = ProjectInfrastructure(
        project_id=project_id,
        **infrastructure.model_dump()
    )
    db.add(new_infrastructure)
    await db.commit()
    await db.refresh(new_infrastructure)
    
    logger.info(f"Infrastruktur-Element zu Projekt {project_id} hinzugefügt")
    return new_infrastructure
