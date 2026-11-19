"""
Energie- und Abrechnungs-Modelle: Stromzähler, Zählerstände, Rechnungen
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Date, Text, DECIMAL
from sqlalchemy.orm import relationship
from typing import List, Optional
from datetime import datetime

from app.database import Base


class ElectricMeter(Base):
    """Stromzähler"""
    __tablename__ = "electric_meter"
    
    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String(36), unique=True, index=True)
    cabinet_id = Column(Integer, ForeignKey("cabinet.id", ondelete="CASCADE"), index=True)
    meter_number = Column(String(50), unique=True, nullable=False, index=True)
    meter_type = Column(String(50))
    installation_date = Column(Date)
    last_calibration_date = Column(Date)
    next_calibration_date = Column(Date)
    status = Column(String(20), default="active")
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Beziehungen
    cabinet: Optional["Cabinet"] = relationship("Cabinet", back_populates="electric_meters")
    meter_readings: List["MeterReading"] = relationship(
        "MeterReading",
        back_populates="meter",
        cascade="all, delete-orphan"
    )
    invoices: List["Invoice"] = relationship(
        "Invoice",
        back_populates="meter",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self):
        return f"<ElectricMeter(id={self.id}, meter_number='{self.meter_number}')>"


class MeterReading(Base):
    """Zählerstand"""
    __tablename__ = "meter_reading"
    
    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String(36), unique=True, index=True)
    meter_id = Column(Integer, ForeignKey("electric_meter.id", ondelete="CASCADE"), index=True)
    reading_date = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    reading_value = Column(DECIMAL(12, 2), nullable=False)  # in kWh
    reading_type = Column(String(20), default="manual")  # manual, automatic, estimated
    recorded_by = Column(Integer, ForeignKey("user_table.id", ondelete="SET NULL"))
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Beziehungen
    meter: Optional[ElectricMeter] = relationship("ElectricMeter", back_populates="meter_readings")
    recorded_by_user: Optional["User"] = relationship("User", foreign_keys=[recorded_by], back_populates="meter_readings")
    
    def __repr__(self):
        return f"<MeterReading(id={self.id}, meter_id={self.meter_id}, reading_date={self.reading_date}, value={self.reading_value})>"
    
    @property
    def consumption_since_last(self) -> Optional[float]:
        """Verbrauch seit der letzten Ablesung"""
        if not self.meter or not self.meter.meter_readings:
            return None
        
        # Sortiere die Ablesungen nach Datum
        sorted_readings = sorted(
            self.meter.meter_readings,
            key=lambda r: r.reading_date
        )
        
        # Finde die vorherige Ablesung
        current_index = sorted_readings.index(self)
        if current_index > 0:
            previous_reading = sorted_readings[current_index - 1]
            return float(self.reading_value - previous_reading.reading_value)
        return None


class Invoice(Base):
    """Rechnung"""
    __tablename__ = "invoice"
    
    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String(36), unique=True, index=True)
    meter_id = Column(Integer, ForeignKey("electric_meter.id", ondelete="SET NULL"), index=True)
    invoice_number = Column(String(50), unique=True, nullable=False, index=True)
    invoice_date = Column(Date, nullable=False)
    due_date = Column(Date)
    period_start = Column(Date)
    period_end = Column(Date)
    consumption = Column(DECIMAL(12, 2))  # Verbrauch in kWh
    unit_price = Column(DECIMAL(10, 4))  # Preis pro kWh in €
    total_amount = Column(DECIMAL(12, 2))  # Gesamtbetrag in €
    tax_rate = Column(DECIMAL(5, 2))  # Steueratz in %
    status = Column(String(20), default="draft")
    payment_date = Column(Date)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Beziehungen
    meter: Optional[ElectricMeter] = relationship("ElectricMeter", back_populates="invoices")
    documents: List["Document"] = relationship(
        "Document",
        foreign_keys="[Document.invoice_id]",
        back_populates="invoice"
    )
    
    def __repr__(self):
        return f"<Invoice(id={self.id}, invoice_number='{self.invoice_number}', amount={self.total_amount})>"
    
    @property
    def tax_amount(self) -> float:
        """Steuerbetrag"""
        if self.total_amount and self.tax_rate:
            return float(self.total_amount) * (float(self.tax_rate) / 100)
        return 0.0
    
    @property
    def net_amount(self) -> float:
        """Nettobetrag (ohne Steuer)"""
        if self.total_amount and self.tax_rate:
            return float(self.total_amount) / (1 + (float(self.tax_rate) / 100))
        return float(self.total_amount) if self.total_amount else 0.0


# Zirkuläre Importe auflösen
from .infrastructure import Cabinet
from .user import User
from .document import Document
