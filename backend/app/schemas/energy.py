"""
Pydantic-Schemas für Energie & Abrechnung
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date
from decimal import Decimal


class ElectricMeterBase(BaseModel):
    """Basis-Schema für Stromzähler"""
    cabinet_id: int = Field(..., description="Schaltschrank-ID")
    meter_number: str = Field(..., min_length=1, max_length=50, description="Zählernummer")
    meter_type: Optional[str] = Field(default=None, max_length=50, description="Zählertyp")
    installation_date: Optional[date] = Field(default=None, description="Installationsdatum")
    last_calibration_date: Optional[date] = Field(default=None, description="Letzte Eichung")
    next_calibration_date: Optional[date] = Field(default=None, description="Nächste Eichung")
    status: str = Field(default="active", description="Status")
    notes: Optional[str] = Field(default=None, description="Notizen")


class ElectricMeterCreate(ElectricMeterBase):
    """Schema zum Erstellen eines Stromzählers"""
    pass


class ElectricMeterUpdate(BaseModel):
    """Schema zum Aktualisieren eines Stromzählers"""
    cabinet_id: Optional[int] = Field(default=None)
    meter_number: Optional[str] = Field(default=None, min_length=1, max_length=50)
    meter_type: Optional[str] = Field(default=None, max_length=50)
    installation_date: Optional[date] = Field(default=None)
    last_calibration_date: Optional[date] = Field(default=None)
    next_calibration_date: Optional[date] = Field(default=None)
    status: Optional[str] = Field(default=None)
    notes: Optional[str] = Field(default=None)


class ElectricMeterResponse(ElectricMeterBase):
    """Response-Schema für Stromzähler"""
    id: int
    uuid: str
    created_at: datetime
    updated_at: datetime
    cabinet: Optional[dict] = None
    meter_readings: List[dict] = Field(default_factory=list)
    invoices: List[dict] = Field(default_factory=list)
    
    class Config:
        from_attributes = True


class MeterReadingBase(BaseModel):
    """Basis-Schema für Zählerstände"""
    reading_date: datetime = Field(..., description="Ablesedatum")
    reading_value: Decimal = Field(..., description="Zählerstand (kWh)")
    reading_type: str = Field(default="manual", description="Ablesetyp")
    recorded_by: Optional[int] = Field(default=None, description="Abgelesen von Benutzer-ID")
    notes: Optional[str] = Field(default=None, description="Notizen")


class MeterReadingCreate(MeterReadingBase):
    """Schema zum Erstellen eines Zählerstands"""
    pass


class MeterReadingUpdate(BaseModel):
    """Schema zum Aktualisieren eines Zählerstands"""
    reading_date: Optional[datetime] = Field(default=None)
    reading_value: Optional[Decimal] = Field(default=None)
    reading_type: Optional[str] = Field(default=None)
    recorded_by: Optional[int] = Field(default=None)
    notes: Optional[str] = Field(default=None)


class MeterReadingResponse(MeterReadingBase):
    """Response-Schema für Zählerstände"""
    id: int
    uuid: str
    meter_id: int
    created_at: datetime
    consumption_since_last: Optional[float] = None
    recorded_by_user: Optional[dict] = None
    
    class Config:
        from_attributes = True


class InvoiceBase(BaseModel):
    """Basis-Schema für Rechnungen"""
    meter_id: Optional[int] = Field(default=None, description="Zähler-ID")
    invoice_number: str = Field(..., min_length=1, max_length=50, description="Rechnungsnummer")
    invoice_date: date = Field(..., description="Rechnungsdatum")
    due_date: Optional[date] = Field(default=None, description="Fälligkeitsdatum")
    period_start: Optional[date] = Field(default=None, description="Abrechnungszeitraum von")
    period_end: Optional[date] = Field(default=None, description="Abrechnungszeitraum bis")
    consumption: Optional[Decimal] = Field(default=None, description="Verbrauch (kWh)")
    unit_price: Optional[Decimal] = Field(default=None, description="Preis pro kWh (€)")
    total_amount: Optional[Decimal] = Field(default=None, description="Gesamtbetrag (€)")
    tax_rate: Optional[Decimal] = Field(default=None, description="Steuersatz (%)")
    status: str = Field(default="draft", description="Status")
    payment_date: Optional[date] = Field(default=None, description="Zahlungsdatum")
    notes: Optional[str] = Field(default=None, description="Notizen")


class InvoiceCreate(InvoiceBase):
    """Schema zum Erstellen einer Rechnung"""
    pass


class InvoiceUpdate(BaseModel):
    """Schema zum Aktualisieren einer Rechnung"""
    meter_id: Optional[int] = Field(default=None)
    invoice_number: Optional[str] = Field(default=None, min_length=1, max_length=50)
    invoice_date: Optional[date] = Field(default=None)
    due_date: Optional[date] = Field(default=None)
    period_start: Optional[date] = Field(default=None)
    period_end: Optional[date] = Field(default=None)
    consumption: Optional[Decimal] = Field(default=None)
    unit_price: Optional[Decimal] = Field(default=None)
    total_amount: Optional[Decimal] = Field(default=None)
    tax_rate: Optional[Decimal] = Field(default=None)
    status: Optional[str] = Field(default=None)
    payment_date: Optional[date] = Field(default=None)
    notes: Optional[str] = Field(default=None)


class InvoiceResponse(InvoiceBase):
    """Response-Schema für Rechnungen"""
    id: int
    uuid: str
    created_at: datetime
    updated_at: datetime
    meter: Optional[dict] = None
    tax_amount: float = 0.0
    net_amount: float = 0.0
    
    class Config:
        from_attributes = True
