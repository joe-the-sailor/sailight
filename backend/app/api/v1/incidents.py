"""
Störungsmeldungen-API
CRUD-Operationen für Störungsmeldungen
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy import and_, or_
from typing import Optional
import logging

from app.database import get_db
from app.models.maintenance import Incident, IncidentType, IncidentStatus
from app.schemas.maintenance import (
    IncidentTypeCreate, IncidentTypeUpdate, IncidentTypeResponse,
    IncidentStatusCreate, IncidentStatusUpdate, IncidentStatusResponse,
    IncidentCreate, IncidentUpdate, IncidentResponse
)
from app.schemas.common import PaginatedResponse, MessageResponse
from app.utils.security import get_current_active_user, require_admin
from app.utils.exceptions import NotFoundException, DuplicateEntryException
from app.utils.pagination import paginate, PaginationParams

router = APIRouter()
logger = logging.getLogger("sailight.incidents")


# =============================================================================
# Störungs-Typen-Endpoints
# =============================================================================

@router.get("/types", response_model=PaginatedResponse[IncidentTypeResponse], summary="Alle Störungs-Typen abrufen")
async def read_incident_types(
    pagination: PaginationParams = Depends(),
    is_active: Optional[bool] = Query(default=None, description="Filter nach Aktivitätsstatus"),
    db: AsyncSession = Depends(get_db),
    current_user: None = Depends(get_current_active_user)
):
    """Ruft alle Störungs-Typen ab"""
    query = select(IncidentType)
    
    if is_active is not None:
        query = query.where(IncidentType.is_active == is_active)
    
    query = query.order_by(IncidentType.name)
    return await paginate(db, query, pagination, IncidentTypeResponse)


@router.post("/types", response_model=IncidentTypeResponse, status_code=status.HTTP_201_CREATED, summary="Störungs-Typ erstellen")
async def create_incident_type(
    incident_type: IncidentTypeCreate,
    db: AsyncSession = Depends(get_db),
    current_user: None = Depends(require_admin)
):
    """Erstellt einen neuen Störungs-Typ"""
    result = await db.execute(
        select(IncidentType).where(IncidentType.name == incident_type.name)
    )
    existing = result.scalar_one_or_none()
    
    if existing:
        raise DuplicateEntryException("Störungs-Typ", incident_type.name)
    
    new_type = IncidentType(**incident_type.model_dump())
    db.add(new_type)
    await db.commit()
    await db.refresh(new_type)
    
    logger.info(f"Störungs-Typ '{incident_type.name}' erstellt")
    return new_type


# =============================================================================
# Störungs-Status-Endpoints
# =============================================================================

@router.get("/statuses", response_model=PaginatedResponse[IncidentStatusResponse], summary="Alle Störungs-Status abrufen")
async def read_incident_statuses(
    pagination: PaginationParams = Depends(),
    is_active: Optional[bool] = Query(default=None, description="Filter nach Aktivitätsstatus"),
    db: AsyncSession = Depends(get_db),
    current_user: None = Depends(get_current_active_user)
):
    """Ruft alle Störungs-Status ab"""
    query = select(IncidentStatus)
    
    if is_active is not None:
        query = query.where(IncidentStatus.is_active == is_active)
    
    query = query.order_by(IncidentStatus.name)
    return await paginate(db, query, pagination, IncidentStatusResponse)


# =============================================================================
# Störungsmeldungen-Endpoints
# =============================================================================

@router.get("/", response_model=PaginatedResponse[IncidentResponse], summary="Alle Störungsmeldungen abrufen")
async def read_incidents(
    pagination: PaginationParams = Depends(),
    search: Optional[str] = Query(default=None, description="Suchbegriff"),
    incident_type_id: Optional[int] = Query(default=None, description="Filter nach Störungs-Typ"),
    incident_status_id: Optional[int] = Query(default=None, description="Filter nach Status"),
    priority: Optional[str] = Query(default=None, description="Filter nach Priorität"),
    light_point_id: Optional[int] = Query(default=None, description="Filter nach Leuchtstelle"),
    pole_id: Optional[int] = Query(default=None, description="Filter nach Mast"),
    cabinet_id: Optional[int] = Query(default=None, description="Filter nach Schaltschrank"),
    reported_by: Optional[int] = Query(default=None, description="Filter nach Meldendem"),
    assigned_to: Optional[int] = Query(default=None, description="Filter nach Zugewiesenen"),
    is_open: Optional[bool] = Query(default=None, description="Filter nach offen/geschlossen"),
    start_date: Optional[str] = Query(default=None, description="Startdatum (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(default=None, description="Enddatum (YYYY-MM-DD)"),
    db: AsyncSession = Depends(get_db),
    current_user: None = Depends(get_current_active_user)
):
    """Ruft alle Störungsmeldungen ab"""
    query = select(Incident).options(
        selectinload(Incident.incident_type),
        selectinload(Incident.incident_status),
        selectinload(Incident.light_point),
        selectinload(Incident.pole),
        selectinload(Incident.cabinet),
        selectinload(Incident.circuit_group),
        selectinload(Incident.reported_by_user),
        selectinload(Incident.assigned_to_user),
        selectinload(Incident.resolved_by_user)
    )
    
    if search:
        query = query.where(
            or_(
                Incident.title.ilike(f"%{search}%"),
                Incident.description.ilike(f"%{search}%"),
                Incident.accident_report_number.ilike(f"%{search}%")
            )
        )
    
    if incident_type_id:
        query = query.where(Incident.incident_type_id == incident_type_id)
    
    if incident_status_id:
        query = query.where(Incident.incident_status_id == incident_status_id)
    
    if priority:
        query = query.where(Incident.priority == priority)
    
    if light_point_id:
        query = query.where(Incident.light_point_id == light_point_id)
    
    if pole_id:
        query = query.where(Incident.pole_id == pole_id)
    
    if cabinet_id:
        query = query.where(Incident.cabinet_id == cabinet_id)
    
    if reported_by:
        query = query.where(Incident.reported_by == reported_by)
    
    if assigned_to:
        query = query.where(Incident.assigned_to == assigned_to)
    
    if is_open is not None:
        if is_open:
            query = query.where(
                Incident.incident_status_id != None
            )
        else:
            query = query.where(
                or_(
                    Incident.incident_status.has(name="Erledigt"),
                    Incident.incident_status.has(name="Storniert")
                )
            )
    
    if start_date:
        query = query.where(Incident.reported_at >= start_date)
    
    if end_date:
        query = query.where(Incident.reported_at <= end_date)
    
    query = query.order_by(Incident.reported_at.desc())
    return await paginate(db, query, pagination, IncidentResponse)


@router.post("/", response_model=IncidentResponse, status_code=status.HTTP_201_CREATED, summary="Störungsmeldung erstellen")
async def create_incident(
    incident: IncidentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: None = Depends(get_current_active_user)
):
    """Erstellt eine neue Störungsmeldung"""
    new_incident = Incident(
        **incident.model_dump(),
        reported_by=current_user.id
    )
    db.add(new_incident)
    await db.commit()
    await db.refresh(new_incident)
    
    logger.info(f"Störungsmeldung '{incident.title}' erstellt von Benutzer {current_user.id}")
    return new_incident


@router.get("/{incident_id}", response_model=IncidentResponse, summary="Störungsmeldung abrufen")
async def read_incident(
    incident_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: None = Depends(get_current_active_user)
):
    """Ruft eine bestimmte Störungsmeldung ab"""
    result = await db.execute(
        select(Incident).where(Incident.id == incident_id)
        .options(
            selectinload(Incident.incident_type),
            selectinload(Incident.incident_status),
            selectinload(Incident.light_point),
            selectinload(Incident.pole),
            selectinload(Incident.cabinet),
            selectinload(Incident.circuit_group),
            selectinload(Incident.reported_by_user),
            selectinload(Incident.assigned_to_user),
            selectinload(Incident.resolved_by_user),
            selectinload(Incident.documents)
        )
    )
    incident = result.scalar_one_or_none()
    
    if not incident:
        raise NotFoundException("Störungsmeldung", incident_id)
    
    return incident


@router.put("/{incident_id}", response_model=IncidentResponse, summary="Störungsmeldung aktualisieren")
async def update_incident(
    incident_id: int,
    incident: IncidentUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: None = Depends(get_current_active_user)
):
    """Aktualisiert eine Störungsmeldung"""
    result = await db.execute(
        select(Incident).where(Incident.id == incident_id)
    )
    existing_incident = result.scalar_one_or_none()
    
    if not existing_incident:
        raise NotFoundException("Störungsmeldung", incident_id)
    
    # Nur Admins oder der Ersteller können die Störung aktualisieren
    if not current_user.has_role("admin") and existing_incident.reported_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Keine Berechtigung, um diese Störungsmeldung zu aktualisieren"
        )
    
    for key, value in incident.model_dump(exclude_unset=True).items():
        setattr(existing_incident, key, value)
    
    await db.commit()
    await db.refresh(existing_incident)
    
    logger.info(f"Störungsmeldung {incident_id} aktualisiert von Benutzer {current_user.id}")
    return existing_incident


@router.post("/{incident_id}/assign", response_model=IncidentResponse, summary="Störung zuweisen")
async def assign_incident(
    incident_id: int,
    assigned_to: int = Query(..., description="Benutzer-ID, dem die Störung zugewiesen wird"),
    db: AsyncSession = Depends(get_db),
    current_user: None = Depends(require_admin)
):
    """Weist eine Störung einem Benutzer zu"""
    result = await db.execute(
        select(Incident).where(Incident.id == incident_id)
    )
    incident = result.scalar_one_or_none()
    
    if not incident:
        raise NotFoundException("Störungsmeldung", incident_id)
    
    incident.assigned_to = assigned_to
    
    # Status auf "In Bearbeitung" setzen, wenn noch nicht
    if incident.incident_status.name == "Gemeldet":
        result = await db.execute(
            select(IncidentStatus).where(IncidentStatus.name == "In Bearbeitung")
        )
        status = result.scalar_one_or_none()
        if status:
            incident.incident_status_id = status.id
    
    await db.commit()
    await db.refresh(incident)
    
    logger.info(f"Störungsmeldung {incident_id} an Benutzer {assigned_to} zugewiesen")
    return incident


@router.post("/{incident_id}/resolve", response_model=IncidentResponse, summary="Störung als erledigt markieren")
async def resolve_incident(
    incident_id: int,
    solution: Optional[str] = Query(default=None, description="Lösung"),
    root_cause: Optional[str] = Query(default=None, description="Ursache"),
    cost: Optional[float] = Query(default=None, description="Kosten"),
    db: AsyncSession = Depends(get_db),
    current_user: None = Depends(get_current_active_user)
):
    """Markiert eine Störung als erledigt"""
    result = await db.execute(
        select(Incident).where(Incident.id == incident_id)
    )
    incident = result.scalar_one_or_none()
    
    if not incident:
        raise NotFoundException("Störungsmeldung", incident_id)
    
    # Status auf "Erledigt" setzen
    result = await db.execute(
        select(IncidentStatus).where(IncidentStatus.name == "Erledigt")
    )
    status = result.scalar_one_or_none()
    
    if not status:
        raise NotFoundException("Status", "Erledigt")
    
    incident.incident_status_id = status.id
    incident.resolved_at = datetime.utcnow()
    incident.resolved_by = current_user.id
    
    if solution:
        incident.solution = solution
    
    if root_cause:
        incident.root_cause = root_cause
    
    if cost:
        incident.cost = cost
    
    await db.commit()
    await db.refresh(incident)
    
    logger.info(f"Störungsmeldung {incident_id} als erledigt markiert von Benutzer {current_user.id}")
    return incident


from datetime import datetime
