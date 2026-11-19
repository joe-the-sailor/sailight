"""
Audit-Log-API
Abfragen für das Audit-Log
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy import and_, or_, desc
from typing import Optional
import logging

from app.database import get_db
from app.models.audit import AuditLog
from app.schemas.audit import AuditLogResponse
from app.schemas.common import PaginatedResponse
from app.utils.security import get_current_active_user, require_admin
from app.utils.pagination import paginate, PaginationParams

router = APIRouter()
logger = logging.getLogger("sailight.audit")


@router.get("/", response_model=PaginatedResponse[AuditLogResponse], summary="Audit-Log abrufen")
async def read_audit_logs(
    pagination: PaginationParams = Depends(),
    user_id: Optional[int] = Query(default=None, description="Filter nach Benutzer"),
    action: Optional[str] = Query(default=None, description="Filter nach Aktion"),
    table_name: Optional[str] = Query(default=None, description="Filter nach Tabelle"),
    record_id: Optional[int] = Query(default=None, description="Filter nach Datensatz-ID"),
    start_date: Optional[str] = Query(default=None, description="Startdatum (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(default=None, description="Enddatum (YYYY-MM-DD)"),
    search: Optional[str] = Query(default=None, description="Suchbegriff"),
    db: AsyncSession = Depends(get_db),
    current_user: None = Depends(require_admin)
):
    """Ruft Audit-Log-Einträge ab (nur für Admins)"""
    query = select(AuditLog).options(
        selectinload(AuditLog.user)
    )
    
    if user_id:
        query = query.where(AuditLog.user_id == user_id)
    
    if action:
        query = query.where(AuditLog.action == action)
    
    if table_name:
        query = query.where(AuditLog.table_name == table_name)
    
    if record_id:
        query = query.where(AuditLog.record_id == record_id)
    
    if start_date:
        query = query.where(AuditLog.created_at >= start_date)
    
    if end_date:
        query = query.where(AuditLog.created_at <= end_date)
    
    if search:
        query = query.where(
            or_(
                AuditLog.table_name.ilike(f"%{search}%"),
                AuditLog.action.ilike(f"%{search}%"),
                AuditLog.ip_address.ilike(f"%{search}%")
            )
        )
    
    query = query.order_by(desc(AuditLog.created_at))
    return await paginate(db, query, pagination, AuditLogResponse)


@router.get("/{audit_log_id}", response_model=AuditLogResponse, summary="Audit-Log-Eintrag abrufen")
async def read_audit_log(
    audit_log_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: None = Depends(require_admin)
):
    """Ruft einen bestimmten Audit-Log-Eintrag ab"""
    result = await db.execute(
        select(AuditLog).where(AuditLog.id == audit_log_id)
        .options(
            selectinload(AuditLog.user)
        )
    )
    audit_log = result.scalar_one_or_none()
    
    if not audit_log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Audit-Log-Eintrag mit ID {audit_log_id} nicht gefunden"
        )
    
    return audit_log


@router.get("/statistics", summary="Audit-Log-Statistiken abrufen")
async def get_audit_log_statistics(
    start_date: Optional[str] = Query(default=None, description="Startdatum (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(default=None, description="Enddatum (YYYY-MM-DD)"),
    db: AsyncSession = Depends(get_db),
    current_user: None = Depends(require_admin)
):
    """Ruft Statistiken für das Audit-Log ab"""
    from sqlalchemy import func, distinct
    
    query = select(AuditLog)
    
    if start_date:
        query = query.where(AuditLog.created_at >= start_date)
    
    if end_date:
        query = query.where(AuditLog.created_at <= end_date)
    
    # Gesamtanzahl
    result = await db.execute(
        select(func.count()).select_from(query.subquery())
    )
    total = result.scalar()
    
    # Anzahl nach Aktion
    result = await db.execute(
        select(
            AuditLog.action,
            func.count(AuditLog.action).label("count")
        )
        .select_from(query.subquery())
        .group_by(AuditLog.action)
    )
    actions = {row.action: row.count for row in result.all()}
    
    # Anzahl nach Tabelle
    result = await db.execute(
        select(
            AuditLog.table_name,
            func.count(AuditLog.table_name).label("count")
        )
        .select_from(query.subquery())
        .group_by(AuditLog.table_name)
    )
    tables = {row.table_name: row.count for row in result.all()}
    
    # Anzahl nach Benutzer
    result = await db.execute(
        select(
            AuditLog.user_id,
            func.count(AuditLog.user_id).label("count")
        )
        .select_from(query.subquery())
        .group_by(AuditLog.user_id)
    )
    users = {row.user_id: row.count for row in result.all()}
    
    return {
        "total": total,
        "by_action": actions,
        "by_table": tables,
        "by_user": users
    }
