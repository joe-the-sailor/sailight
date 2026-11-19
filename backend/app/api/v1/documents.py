"""
Dokumentenmanagement-API
CRUD-Operationen für Dokumente
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from typing import Optional
import logging
import os

from app.database import get_db
from app.models.document import Document, DocumentType
from app.schemas.document import (
    DocumentTypeCreate, DocumentTypeUpdate, DocumentTypeResponse,
    DocumentCreate, DocumentUpdate, DocumentResponse
)
from app.schemas.common import PaginatedResponse, MessageResponse
from app.utils.security import get_current_active_user, require_admin
from app.utils.exceptions import NotFoundException, DuplicateEntryException, FileUploadException
from app.utils.pagination import paginate, PaginationParams
from app.utils.file_upload import save_upload_file, delete_file
from app.config import settings

router = APIRouter()
logger = logging.getLogger("sailight.documents")


# =============================================================================
# Dokumenten-Typen-Endpoints
# =============================================================================

@router.get("/types", response_model=PaginatedResponse[DocumentTypeResponse], summary="Alle Dokumenten-Typen abrufen")
async def read_document_types(
    pagination: PaginationParams = Depends(),
    is_active: Optional[bool] = Query(default=None, description="Filter nach Aktivitätsstatus"),
    db: AsyncSession = Depends(get_db),
    current_user: None = Depends(get_current_active_user)
):
    """Ruft alle Dokumenten-Typen ab"""
    query = select(DocumentType)
    
    if is_active is not None:
        query = query.where(DocumentType.is_active == is_active)
    
    query = query.order_by(DocumentType.name)
    return await paginate(db, query, pagination, DocumentTypeResponse)


@router.post("/types", response_model=DocumentTypeResponse, status_code=status.HTTP_201_CREATED, summary="Dokumenten-Typ erstellen")
async def create_document_type(
    document_type: DocumentTypeCreate,
    db: AsyncSession = Depends(get_db),
    current_user: None = Depends(require_admin)
):
    """Erstellt einen neuen Dokumenten-Typ"""
    result = await db.execute(
        select(DocumentType).where(DocumentType.name == document_type.name)
    )
    existing = result.scalar_one_or_none()
    
    if existing:
        raise DuplicateEntryException("Dokumenten-Typ", document_type.name)
    
    new_type = DocumentType(**document_type.model_dump())
    db.add(new_type)
    await db.commit()
    await db.refresh(new_type)
    
    logger.info(f"Dokumenten-Typ '{document_type.name}' erstellt")
    return new_type


# =============================================================================
# Dokumente-Endpoints
# =============================================================================

@router.get("/", response_model=PaginatedResponse[DocumentResponse], summary="Alle Dokumente abrufen")
async def read_documents(
    pagination: PaginationParams = Depends(),
    search: Optional[str] = Query(default=None, description="Suchbegriff"),
    document_type_id: Optional[int] = Query(default=None, description="Filter nach Dokumenten-Typ"),
    light_point_id: Optional[int] = Query(default=None, description="Filter nach Leuchtstelle"),
    pole_id: Optional[int] = Query(default=None, description="Filter nach Mast"),
    cabinet_id: Optional[int] = Query(default=None, description="Filter nach Schaltschrank"),
    circuit_group_id: Optional[int] = Query(default=None, description="Filter nach Leitungsgruppe"),
    incident_id: Optional[int] = Query(default=None, description="Filter nach Störung"),
    project_id: Optional[int] = Query(default=None, description="Filter nach Projekt"),
    invoice_id: Optional[int] = Query(default=None, description="Filter nach Rechnung"),
    db: AsyncSession = Depends(get_db),
    current_user: None = Depends(get_current_active_user)
):
    """Ruft alle Dokumente ab"""
    query = select(Document).options(
        selectinload(Document.document_type),
        selectinload(Document.uploaded_by_user),
        selectinload(Document.light_point),
        selectinload(Document.pole),
        selectinload(Document.cabinet),
        selectinload(Document.circuit_group),
        selectinload(Document.incident),
        selectinload(Document.project),
        selectinload(Document.invoice)
    )
    
    if search:
        query = query.where(
            Document.title.ilike(f"%{search}%") |
            Document.description.ilike(f"%{search}%") |
            Document.file_name.ilike(f"%{search}%")
        )
    
    if document_type_id:
        query = query.where(Document.document_type_id == document_type_id)
    
    if light_point_id:
        query = query.where(Document.light_point_id == light_point_id)
    
    if pole_id:
        query = query.where(Document.pole_id == pole_id)
    
    if cabinet_id:
        query = query.where(Document.cabinet_id == cabinet_id)
    
    if circuit_group_id:
        query = query.where(Document.circuit_group_id == circuit_group_id)
    
    if incident_id:
        query = query.where(Document.incident_id == incident_id)
    
    if project_id:
        query = query.where(Document.project_id == project_id)
    
    if invoice_id:
        query = query.where(Document.invoice_id == invoice_id)
    
    query = query.order_by(Document.uploaded_at.desc())
    return await paginate(db, query, pagination, DocumentResponse)


@router.post("/upload", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED, summary="Dokument hochladen")
async def upload_document(
    file: UploadFile = File(..., description="Datei"),
    document_type_id: int = Query(..., description="Dokumenten-Typ-ID"),
    title: str = Query(..., description="Titel"),
    description: Optional[str] = Query(default=None, description="Beschreibung"),
    light_point_id: Optional[int] = Query(default=None, description="Leuchtstellen-ID"),
    pole_id: Optional[int] = Query(default=None, description="Mast-ID"),
    cabinet_id: Optional[int] = Query(default=None, description="Schaltschrank-ID"),
    circuit_group_id: Optional[int] = Query(default=None, description="Leitungsgruppen-ID"),
    incident_id: Optional[int] = Query(default=None, description="Störungs-ID"),
    project_id: Optional[int] = Query(default=None, description="Projekt-ID"),
    invoice_id: Optional[int] = Query(default=None, description="Rechnungs-ID"),
    db: AsyncSession = Depends(get_db),
    current_user: None = Depends(get_current_active_user)
):
    """Lädt ein Dokument hoch"""
    # Datei validieren
    if not file.filename:
        raise FileUploadException("Kein Dateiname angegeben")
    
    # Datei speichern
    file_path, original_filename, file_size = await save_upload_file(file)
    
    # Dateityp bestimmen
    mime_type = file.content_type or "application/octet-stream"
    
    # Dokument erstellen
    new_document = Document(
        document_type_id=document_type_id,
        title=title,
        description=description,
        file_path=file_path,
        file_name=original_filename,
        file_size=file_size,
        mime_type=mime_type,
        uploaded_by=current_user.id,
        light_point_id=light_point_id,
        pole_id=pole_id,
        cabinet_id=cabinet_id,
        circuit_group_id=circuit_group_id,
        incident_id=incident_id,
        project_id=project_id,
        invoice_id=invoice_id
    )
    
    db.add(new_document)
    await db.commit()
    await db.refresh(new_document)
    
    logger.info(f"Dokument '{title}' hochgeladen von Benutzer {current_user.id}")
    return new_document


@router.get("/{document_id}", response_model=DocumentResponse, summary="Dokument abrufen")
async def read_document(
    document_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: None = Depends(get_current_active_user)
):
    """Ruft ein bestimmtes Dokument ab"""
    result = await db.execute(
        select(Document).where(Document.id == document_id)
        .options(
            selectinload(Document.document_type),
            selectinload(Document.uploaded_by_user),
            selectinload(Document.light_point),
            selectinload(Document.pole),
            selectinload(Document.cabinet),
            selectinload(Document.circuit_group),
            selectinload(Document.incident),
            selectinload(Document.project),
            selectinload(Document.invoice)
        )
    )
    document = result.scalar_one_or_none()
    
    if not document:
        raise NotFoundException("Dokument", document_id)
    
    return document


@router.get("/{document_id}/download", summary="Dokument herunterladen")
async def download_document(
    document_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: None = Depends(get_current_active_user)
):
    """Lädt ein Dokument herunter"""
    result = await db.execute(
        select(Document).where(Document.id == document_id)
    )
    document = result.scalar_one_or_none()
    
    if not document:
        raise NotFoundException("Dokument", document_id)
    
    # Dateipfad prüfen
    if not os.path.exists(document.file_path):
        raise NotFoundException("Datei", document_id)
    
    # Datei zurückgeben
    from fastapi.responses import FileResponse
    return FileResponse(
        path=document.file_path,
        filename=document.file_name,
        media_type=document.mime_type
    )


@router.delete("/{document_id}", response_model=MessageResponse, summary="Dokument löschen")
async def delete_document(
    document_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: None = Depends(require_admin)
):
    """Löscht ein Dokument"""
    result = await db.execute(
        select(Document).where(Document.id == document_id)
    )
    document = result.scalar_one_or_none()
    
    if not document:
        raise NotFoundException("Dokument", document_id)
    
    # Datei löschen
    await delete_file(document.file_path)
    
    # Dokument aus der Datenbank löschen
    await db.delete(document)
    await db.commit()
    
    logger.info(f"Dokument {document_id} gelöscht")
    return MessageResponse(message=f"Dokument '{document.title}' wurde gelöscht")
