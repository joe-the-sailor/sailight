"""
Benutzer-API
CRUD-Operationen für Benutzer und Rollen
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy import and_, or_
from typing import List, Optional
import logging

from app.database import get_db
from app.models.user import User, Role, UserRole
from app.models.audit import AuditLog
from app.schemas.user import (
    UserCreate, UserUpdate, UserResponse, UserListResponse,
    RoleCreate, RoleUpdate, RoleResponse,
    TokenResponse
)
from app.schemas.common import PaginatedResponse, MessageResponse
from app.utils.security import (
    get_current_active_user, get_current_user_with_roles,
    require_admin, has_role, get_password_hash
)
from app.utils.exceptions import (
    NotFoundException, DuplicateEntryException, PermissionDeniedException
)
from app.utils.pagination import paginate, PaginationParams

router = APIRouter()
logger = logging.getLogger("sailight.users")


# =============================================================================
# Rollen-Endpoints
# =============================================================================

@router.get("/roles", response_model=PaginatedResponse[RoleResponse], summary="Alle Rollen abrufen")
async def read_roles(
    pagination: PaginationParams = Depends(),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Ruft alle Rollen ab (nur für Admins)"""
    query = select(Role).order_by(Role.name)
    return await paginate(db, query, pagination, RoleResponse)


@router.post("/roles", response_model=RoleResponse, status_code=status.HTTP_201_CREATED, summary="Rolle erstellen")
async def create_role(
    role: RoleCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Erstellt eine neue Rolle (nur für Admins)"""
    # Prüfen, ob Rolle bereits existiert
    result = await db.execute(
        select(Role).where(Role.name == role.name)
    )
    existing_role = result.scalar_one_or_none()
    
    if existing_role:
        raise DuplicateEntryException("Rolle", role.name)
    
    # Neue Rolle erstellen
    new_role = Role(**role.model_dump())
    db.add(new_role)
    await db.commit()
    await db.refresh(new_role)
    
    logger.info(f"Rolle '{role.name}' erstellt von Benutzer {current_user.id}")
    return new_role


@router.get("/roles/{role_id}", response_model=RoleResponse, summary="Rolle abrufen")
async def read_role(
    role_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Ruft eine bestimmte Rolle ab"""
    result = await db.execute(
        select(Role).where(Role.id == role_id)
    )
    role = result.scalar_one_or_none()
    
    if not role:
        raise NotFoundException("Rolle", role_id)
    
    return role


@router.put("/roles/{role_id}", response_model=RoleResponse, summary="Rolle aktualisieren")
async def update_role(
    role_id: int,
    role: RoleUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Aktualisiert eine Rolle"""
    result = await db.execute(
        select(Role).where(Role.id == role_id)
    )
    existing_role = result.scalar_one_or_none()
    
    if not existing_role:
        raise NotFoundException("Rolle", role_id)
    
    # Aktualisieren
    for key, value in role.model_dump(exclude_unset=True).items():
        setattr(existing_role, key, value)
    
    await db.commit()
    await db.refresh(existing_role)
    
    logger.info(f"Rolle {role_id} aktualisiert von Benutzer {current_user.id}")
    return existing_role


@router.delete("/roles/{role_id}", response_model=MessageResponse, summary="Rolle löschen")
async def delete_role(
    role_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Löscht eine Rolle"""
    result = await db.execute(
        select(Role).where(Role.id == role_id)
    )
    role = result.scalar_one_or_none()
    
    if not role:
        raise NotFoundException("Rolle", role_id)
    
    await db.delete(role)
    await db.commit()
    
    logger.info(f"Rolle {role_id} gelöscht von Benutzer {current_user.id}")
    return MessageResponse(message=f"Rolle '{role.name}' wurde gelöscht")


# =============================================================================
# Benutzer-Endpoints
# =============================================================================

@router.get("/", response_model=PaginatedResponse[UserListResponse], summary="Alle Benutzer abrufen")
async def read_users(
    pagination: PaginationParams = Depends(),
    search: Optional[str] = Query(default=None, description="Suchbegriff"),
    is_active: Optional[bool] = Query(default=None, description="Filter nach Aktivitätsstatus"),
    role: Optional[str] = Query(default=None, description="Filter nach Rolle"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Ruft alle Benutzer ab (nur für Admins)"""
    query = select(User).options(selectinload(User.roles))
    
    # Filter anwenden
    if search:
        query = query.where(
            or_(
                User.username.ilike(f"%{search}%"),
                User.email.ilike(f"%{search}%"),
                User.first_name.ilike(f"%{search}%"),
                User.last_name.ilike(f"%{search}%")
            )
        )
    
    if is_active is not None:
        query = query.where(User.is_active == is_active)
    
    if role:
        # Filter nach Rolle (über die Beziehung)
        query = query.join(User.roles).where(Role.name == role)
    
    query = query.order_by(User.username)
    
    return await paginate(db, query, pagination, UserListResponse)


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED, summary="Benutzer erstellen")
async def create_user(
    user: UserCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Erstellt einen neuen Benutzer (nur für Admins)"""
    # Prüfen, ob Benutzername bereits existiert
    result = await db.execute(
        select(User).where(User.username == user.username)
    )
    existing_user = result.scalar_one_or_none()
    
    if existing_user:
        raise DuplicateEntryException("Benutzername", user.username)
    
    # Prüfen, ob E-Mail bereits existiert
    result = await db.execute(
        select(User).where(User.email == user.email)
    )
    existing_email = result.scalar_one_or_none()
    
    if existing_email:
        raise DuplicateEntryException("E-Mail", user.email)
    
    # Passwort hashen
    hashed_password = get_password_hash(user.password)
    
    # Benutzer erstellen
    new_user = User(
        username=user.username,
        email=user.email,
        password_hash=hashed_password,
        first_name=user.first_name,
        last_name=user.last_name,
        phone=user.phone,
        department=user.department,
        is_active=user.is_active
    )
    
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    # Rollen zuweisen
    if user.role_ids:
        for role_id in user.role_ids:
            result = await db.execute(
                select(Role).where(Role.id == role_id)
            )
            role = result.scalar_one_or_none()
            
            if role:
                user_role = UserRole(user_id=new_user.id, role_id=role.id)
                db.add(user_role)
        
        await db.commit()
        await db.refresh(new_user)
    
    # Benutzer mit Rollen neu laden
    await db.refresh(new_user)
    
    logger.info(f"Benutzer '{user.username}' erstellt von Benutzer {current_user.id}")
    return new_user


@router.get("/{user_id}", response_model=UserResponse, summary="Benutzer abrufen")
async def read_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Ruft einen bestimmten Benutzer ab"""
    # Admin kann alle Benutzer abrufen, andere nur sich selbst
    if not has_role(current_user, "admin") and current_user.id != user_id:
        raise PermissionDeniedException("Keine Berechtigung, um diesen Benutzer zu lesen")
    
    result = await db.execute(
        select(User).where(User.id == user_id)
        .options(selectinload(User.roles))
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise NotFoundException("Benutzer", user_id)
    
    return user


@router.put("/{user_id}", response_model=UserResponse, summary="Benutzer aktualisieren")
async def update_user(
    user_id: int,
    user: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Aktualisiert einen Benutzer"""
    # Admin kann alle Benutzer aktualisieren, andere nur sich selbst
    if not has_role(current_user, "admin") and current_user.id != user_id:
        raise PermissionDeniedException("Keine Berechtigung, um diesen Benutzer zu aktualisieren")
    
    result = await db.execute(
        select(User).where(User.id == user_id)
        .options(selectinload(User.roles))
    )
    existing_user = result.scalar_one_or_none()
    
    if not existing_user:
        raise NotFoundException("Benutzer", user_id)
    
    # Prüfen, ob Benutzername bereits existiert (wenn geändert)
    if user.username and user.username != existing_user.username:
        result = await db.execute(
            select(User).where(User.username == user.username, User.id != user_id)
        )
        existing_username = result.scalar_one_or_none()
        
        if existing_username:
            raise DuplicateEntryException("Benutzername", user.username)
    
    # Prüfen, ob E-Mail bereits existiert (wenn geändert)
    if user.email and user.email != existing_user.email:
        result = await db.execute(
            select(User).where(User.email == user.email, User.id != user_id)
        )
        existing_email = result.scalar_one_or_none()
        
        if existing_email:
            raise DuplicateEntryException("E-Mail", user.email)
    
    # Aktualisieren
    for key, value in user.model_dump(exclude_unset=True, exclude=["password", "role_ids"]).items():
        setattr(existing_user, key, value)
    
    # Passwort aktualisieren (falls angegeben)
    if user.password:
        existing_user.password_hash = get_password_hash(user.password)
    
    await db.commit()
    await db.refresh(existing_user)
    
    # Rollen aktualisieren (falls angegeben)
    if user.role_ids is not None:
        # Aktuelle Rollen löschen
        await db.execute(
            UserRole.__table__.delete().where(UserRole.user_id == user_id)
        )
        
        # Neue Rollen hinzufügen
        for role_id in user.role_ids:
            result = await db.execute(
                select(Role).where(Role.id == role_id)
            )
            role = result.scalar_one_or_none()
            
            if role:
                user_role = UserRole(user_id=user_id, role_id=role.id)
                db.add(user_role)
        
        await db.commit()
        await db.refresh(existing_user)
    
    logger.info(f"Benutzer {user_id} aktualisiert von Benutzer {current_user.id}")
    return existing_user


@router.delete("/{user_id}", response_model=MessageResponse, summary="Benutzer löschen")
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Löscht einen Benutzer (nur für Admins)"""
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise NotFoundException("Benutzer", user_id)
    
    # Benutzer nicht wirklich löschen, sondern nur deaktivieren
    user.is_active = False
    await db.commit()
    
    logger.info(f"Benutzer {user_id} deaktiviert von Benutzer {current_user.id}")
    return MessageResponse(message=f"Benutzer '{user.username}' wurde deaktiviert")
