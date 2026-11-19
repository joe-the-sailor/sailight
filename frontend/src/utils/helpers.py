"""
Hilfsfunktionen für die Frontend-Anwendung
"""

from datetime import datetime, date
from decimal import Decimal
from typing import Any, Optional
import re
import uuid


def format_date(date_value: Any, format: str = "%d.%m.%Y") -> str:
    """
    Formatiert ein Datum
    
    Args:
        date_value: Datum (str, date, datetime)
        format: Format-String
    
    Returns:
        Formatiertes Datum als String
    """
    if not date_value:
        return ""
    
    try:
        if isinstance(date_value, str):
            # ISO-Format parsen
            if date_value.endswith("Z"):
                date_value = date_value[:-1] + "+00:00"
            parsed_date = datetime.fromisoformat(date_value)
        elif isinstance(date_value, (date, datetime)):
            parsed_date = date_value
        else:
            return str(date_value)
        
        return parsed_date.strftime(format)
    except (ValueError, TypeError):
        return str(date_value)


def format_datetime(datetime_value: Any, format: str = "%d.%m.%Y %H:%M:%S") -> str:
    """
    Formatiert ein Datum mit Uhrzeit
    
    Args:
        datetime_value: Datum mit Uhrzeit (str, datetime)
        format: Format-String
    
    Returns:
        Formatiertes Datum als String
    """
    if not datetime_value:
        return ""
    
    try:
        if isinstance(datetime_value, str):
            if datetime_value.endswith("Z"):
                datetime_value = datetime_value[:-1] + "+00:00"
            parsed_datetime = datetime.fromisoformat(datetime_value)
        elif isinstance(datetime_value, datetime):
            parsed_datetime = datetime_value
        else:
            return str(datetime_value)
        
        return parsed_datetime.strftime(format)
    except (ValueError, TypeError):
        return str(datetime_value)


def format_number(number: Any, decimals: int = 2, thousand_sep: str = ".", decimal_sep: str = ",") -> str:
    """
    Formatiert eine Zahl
    
    Args:
        number: Zahl (int, float, Decimal, str)
        decimals: Anzahl der Dezimalstellen
        thousand_sep: Tausendertrennzeichen
        decimal_sep: Dezimaltrennzeichen
    
    Returns:
        Formatierte Zahl als String
    """
    if not number:
        return ""
    
    try:
        if isinstance(number, str):
            number = Decimal(number)
        elif isinstance(number, (int, float)):
            number = Decimal(str(number))
        elif isinstance(number, Decimal):
            pass
        else:
            return str(number)
        
        # Formatieren
        format_str = f"{thousand_sep}0f" if decimals == 0 else f"{thousand_sep}0.{decimals}f"
        formatted = format(number, format_str)
        
        # Tausendertrennzeichen ersetzen
        if thousand_sep != ".":
            formatted = formatted.replace(".", thousand_sep)
        
        # Dezimaltrennzeichen ersetzen
        if decimal_sep != ",":
            formatted = formatted.replace(",", decimal_sep)
        
        return formatted
    except (ValueError, TypeError, InvalidOperation):
        return str(number)


def format_currency(amount: Any, currency: str = "€", decimals: int = 2) -> str:
    """
    Formatiert einen Betrag als Währung
    
    Args:
        amount: Betrag (int, float, Decimal, str)
        currency: Währungssymbol
        decimals: Anzahl der Dezimalstellen
    
    Returns:
        Formatierter Betrag als String
    """
    if not amount:
        return ""
    
    try:
        formatted_amount = format_number(amount, decimals)
        return f"{formatted_amount} {currency}"
    except (ValueError, TypeError):
        return str(amount)


def truncate_text(text: str, max_length: int = 50, suffix: str = "...") -> str:
    """
    Kürzt einen Text
    
    Args:
        text: Text
        max_length: Maximale Länge
        suffix: Suffix für gekürzten Text
    
    Returns:
        Gekürzter Text
    """
    if not text:
        return ""
    
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix


def generate_id(prefix: str = "", length: int = 8) -> str:
    """
    Erzeugt eine eindeutige ID
    
    Args:
        prefix: Präfix
        length: Länge des zufälligen Teils
    
    Returns:
        Eindeutige ID
    """
    unique_id = str(uuid.uuid4())[:length]
    return f"{prefix}{unique_id}" if prefix else unique_id


def validate_email(email: str) -> bool:
    """
    Validiert eine E-Mail-Adresse
    
    Args:
        email: E-Mail-Adresse
    
    Returns:
        True wenn gültig, False sonst
    """
    if not email:
        return False
    
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(pattern, email) is not None


def validate_phone(phone: str) -> bool:
    """
    Validiert eine Telefonnummer
    
    Args:
        phone: Telefonnummer
    
    Returns:
        True wenn gültig, False sonst
    """
    if not phone:
        return False
    
    # Einfache Validierung: nur Zahlen und bestimmte Sonderzeichen
    pattern = r"^[+0-9\-\s\(\)]{6,20}$"
    return re.match(pattern, phone) is not None


def format_bytes(size: int) -> str:
    """
    Formatiert eine Dateigröße in Bytes
    
    Args:
        size: Größe in Bytes
    
    Returns:
        Formatierte Größe (z.B. "1.2 MB")
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024.0:
            return f"{size:.1f} {unit}"
        size /= 1024.0
    return f"{size:.1f} PB"
