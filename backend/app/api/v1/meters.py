"""
Stromzähler-API
CRUD-Operationen für Stromzähler, Zählerstände und Rechnungen
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from typing import Optional
import logging

from app.database import get_db
from app.models.energy import ElectricMeter, MeterReading, Invoice
from app.schemas.energy import (
    ElectricMeterCreate, ElectricMeterUpdate, ElectricMeterResponse,
    MeterReadingCreate, MeterReadingUpdate, MeterReadingResponse,
    InvoiceCreate, InvoiceUpdate, InvoiceResponse
)
from app.schemas.common import PaginatedResponse, MessageResponse
from app.utils.security import get_current_active_user, require_admin
from app.utils.exceptions import NotFoundException, DuplicateEntryException
from app.utils.pagination import paginate, PaginationParams

router = APIRouter()
logger = logging.getLogger("sailight.meters")


# =============================================================================
# Stromzähler-Endpoints
# =============================================================================

@router.get("/", response_model=PaginatedResponse[ElectricMeterResponse], summary="Alle Stromzähler abrufen")
async def read_meters(
    pagination: PaginationParams = Depends(),
    cabinet_id: Optional[int] = Query(default=None, description="Filter nach Schaltschrank"),
    search: Optional[str] = Query(default=None, description="Suchbegriff"),
    status: Optional[str] = Query(default=None, description="Filter nach Status"),
    db: AsyncSession = Depends(get_db),
    current_user: None = Depends(get_current_active_user)
):
    """Ruft alle Stromzähler ab"""
    query = select(ElectricMeter).options(
        selectinload(ElectricMeter.cabinet),
        selectinload(ElectricMeter.meter_readings),
        selectinload(ElectricMeter.invoices)
    )
    
    if cabinet_id:
        query = query.where(ElectricMeter.cabinet_id == cabinet_id)
    
    if search:
        query = query.where(
            ElectricMeter.meter_number.ilike(f"%{search}%")
        )
    
    if status:
        query = query.where(ElectricMeter.status == status)
    
    query = query.order_by(ElectricMeter.meter_number)
    return await paginate(db, query, pagination, ElectricMeterResponse)


@router.post("/", response_model=ElectricMeterResponse, status_code=status.HTTP_201_CREATED, summary="Stromzähler erstellen")
async def create_meter(
    meter: ElectricMeterCreate,
    db: AsyncSession = Depends(get_db),
    current_user: None = Depends(require_admin)
):
    """Erstellt einen neuen Stromzähler"""
    result = await db.execute(
        select(ElectricMeter).where(ElectricMeter.meter_number == meter.meter_number)
    )
    existing = result.scalar_one_or_none()
    
    if existing:
        raise DuplicateEntryException("Zählernummer", meter.meter_number)
    
    new_meter = ElectricMeter(**meter.model_dump())
    db.add(new_meter)
    await db.commit()
    await db.refresh(new_meter)
    
    logger.info(f"Stromzähler '{meter.meter_number}' erstellt")
    return new_meter


@router.get("/{meter_id}", response_model=ElectricMeterResponse, summary="Stromzähler abrufen")
async def read_meter(
    meter_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: None = Depends(get_current_active_user)
):
    """Ruft einen bestimmten Stromzähler ab"""
    result = await db.execute(
        select(ElectricMeter).where(ElectricMeter.id == meter_id)
        .options(
            selectinload(ElectricMeter.cabinet),
            selectinload(ElectricMeter.meter_readings),
            selectinload(ElectricMeter.invoices)
        )
    )
    meter = result.scalar_one_or_none()
    
    if not meter:
        raise NotFoundException("Stromzähler", meter_id)
    
    return meter


@router.put("/{meter_id}", response_model=ElectricMeterResponse, summary="Stromzähler aktualisieren")
async def update_meter(
    meter_id: int,
    meter: ElectricMeterUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: None = Depends(require_admin)
):
    """Aktualisiert einen Stromzähler"""
    result = await db.execute(
        select(ElectricMeter).where(ElectricMeter.id == meter_id)
    )
    existing_meter = result.scalar_one_or_none()
    
    if not existing_meter:
        raise NotFoundException("Stromzähler", meter_id)
    
    if meter.meter_number and meter.meter_number != existing_meter.meter_number:
        result = await db.execute(
            select(ElectricMeter).where(
                ElectricMeter.meter_number == meter.meter_number,
                ElectricMeter.id != meter_id
            )
        )
        existing = result.scalar_one_or_none()
        
        if existing:
            raise DuplicateEntryException("Zählernummer", meter.meter_number)
    
    for key, value in meter.model_dump(exclude_unset=True).items():
        setattr(existing_meter, key, value)
    
    await db.commit()
    await db.refresh(existing_meter)
    
    logger.info(f"Stromzähler {meter_id} aktualisiert")
    return existing_meter


# =============================================================================
# Zählerstände-Endpoints
# =============================================================================

@router.get("/{meter_id}/readings", response_model=PaginatedResponse[MeterReadingResponse], summary="Zählerstände abrufen")
async def read_meter_readings(
    meter_id: int,
    pagination: PaginationParams = Depends(),
    start_date: Optional[str] = Query(default=None, description="Startdatum (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(default=None, description="Enddatum (YYYY-MM-DD)"),
    db: AsyncSession = Depends(get_db),
    current_user: None = Depends(get_current_active_user)
):
    """Ruft alle Zählerstände für einen Zähler ab"""
    result = await db.execute(
        select(ElectricMeter).where(ElectricMeter.id == meter_id)
    )
    meter = result.scalar_one_or_none()
    
    if not meter:
        raise NotFoundException("Stromzähler", meter_id)
    
    query = select(MeterReading).where(MeterReading.meter_id == meter_id)
    
    if start_date:
        query = query.where(MeterReading.reading_date >= start_date)
    
    if end_date:
        query = query.where(MeterReading.reading_date <= end_date)
    
    query = query.order_by(MeterReading.reading_date.desc())
    return await paginate(db, query, pagination, MeterReadingResponse)


@router.post("/{meter_id}/readings", response_model=MeterReadingResponse, status_code=status.HTTP_201_CREATED, summary="Zählerstand erstellen")
async def create_meter_reading(
    meter_id: int,
    reading: MeterReadingCreate,
    db: AsyncSession = Depends(get_db),
    current_user: None = Depends(get_current_active_user)
):
    """Erstellt einen neuen Zählerstand"""
    result = await db.execute(
        select(ElectricMeter).where(ElectricMeter.id == meter_id)
    )
    meter = result.scalar_one_or_none()
    
    if not meter:
        raise NotFoundException("Stromzähler", meter_id)
    
    new_reading = MeterReading(
        meter_id=meter_id,
        **reading.model_dump()
    )
    db.add(new_reading)
    await db.commit()
    await db.refresh(new_reading)
    
    logger.info(f"Zählerstand für Zähler {meter_id} erstellt")
    return new_reading


# =============================================================================
# Rechnungen-Endpoints
# =============================================================================

@router.get("/invoices", response_model=PaginatedResponse[InvoiceResponse], summary="Alle Rechnungen abrufen")
async def read_invoices(
    pagination: PaginationParams = Depends(),
    meter_id: Optional[int] = Query(default=None, description="Filter nach Zähler"),
    status: Optional[str] = Query(default=None, description="Filter nach Status"),
    start_date: Optional[str] = Query(default=None, description="Startdatum (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(default=None, description="Enddatum (YYYY-MM-DD)"),
    db: AsyncSession = Depends(get_db),
    current_user: None = Depends(get_current_active_user)
):
    """Ruft alle Rechnungen ab"""
    query = select(Invoice).options(
        selectinload(Invoice.meter)
    )
    
    if meter_id:
        query = query.where(Invoice.meter_id == meter_id)
    
    if status:
        query = query.where(Invoice.status == status)
    
    if start_date:
        query = query.where(Invoice.invoice_date >= start_date)
    
    if end_date:
        query = query.where(Invoice.invoice_date <= end_date)
    
    query = query.order_by(Invoice.invoice_date.desc())
    return await paginate(db, query, pagination, InvoiceResponse)


@router.post("/invoices", response_model=InvoiceResponse, status_code=status.HTTP_201_CREATED, summary="Rechnung erstellen")
async def create_invoice(
    invoice: InvoiceCreate,
    db: AsyncSession = Depends(get_db),
    current_user: None = Depends(require_admin)
):
    """Erstellt eine neue Rechnung"""
    result = await db.execute(
        select(Invoice).where(Invoice.invoice_number == invoice.invoice_number)
    )
    existing = result.scalar_one_or_none()
    
    if existing:
        raise DuplicateEntryException("Rechnungsnummer", invoice.invoice_number)
    
    new_invoice = Invoice(**invoice.model_dump())
    db.add(new_invoice)
    await db.commit()
    await db.refresh(new_invoice)
    
    logger.info(f"Rechnung '{invoice.invoice_number}' erstellt")
    return new_invoice


@router.get("/invoices/{invoice_id}", response_model=InvoiceResponse, summary="Rechnung abrufen")
async def read_invoice(
    invoice_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: None = Depends(get_current_active_user)
):
    """Ruft eine bestimmte Rechnung ab"""
    result = await db.execute(
        select(Invoice).where(Invoice.id == invoice_id)
        .options(
            selectinload(Invoice.meter)
        )
    )
    invoice = result.scalar_one_or_none()
    
    if not invoice:
        raise NotFoundException("Rechnung", invoice_id)
    
    return invoice
