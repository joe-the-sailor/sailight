"""
Datei-Upload-Utilities
"""

import os
import uuid
from pathlib import Path
from typing import Optional, Tuple
from datetime import datetime
import logging

from fastapi import UploadFile, HTTPException, status
from app.config import settings
from app.utils.exceptions import FileUploadException

logger = logging.getLogger("sailight.file_upload")


def validate_file_extension(file: UploadFile) -> bool:
    """
    Validiert die Dateiendung
    
    Args:
        file: UploadFile-Objekt
    
    Returns:
        True wenn die Dateiendung erlaubt ist
    
    Raises:
        FileUploadException: Wenn die Dateiendung nicht erlaubt ist
    """
    filename = file.filename or ""
    extension = filename.split(".")[-1].lower()
    
    if extension not in settings.ALLOWED_EXTENSIONS:
        raise FileUploadException(
            f"Dateiendung '{extension}' ist nicht erlaubt. Erlaubte Endungen: {', '.join(settings.ALLOWED_EXTENSIONS)}"
        )
    
    return True


def generate_file_name(original_filename: str) -> str:
    """
    Erzeugt einen einzigartigen Dateinamen
    
    Args:
        original_filename: Originaler Dateiname
    
    Returns:
        Einzigartiger Dateiname
    """
    extension = original_filename.split(".")[-1].lower()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_id = str(uuid.uuid4())[:8]
    
    return f"{timestamp}_{unique_id}.{extension}"


def get_file_size(file: UploadFile) -> int:
    """
    Gibt die Dateigröße in Bytes zurück
    
    Args:
        file: UploadFile-Objekt
    
    Returns:
        Dateigröße in Bytes
    """
    # Datei-Inhalt lesen und Größe bestimmen
    content = file.file.read()
    file.file.seek(0)  # Zurück zum Anfang
    return len(content)


async def save_upload_file(
    file: UploadFile,
    subdirectory: Optional[str] = None
) -> Tuple[str, str, int]:
    """
    Speichert eine hochgeladene Datei
    
    Args:
        file: UploadFile-Objekt
        subdirectory: Unterverzeichnis (optional)
    
    Returns:
        Tuple aus (file_path, file_name, file_size)
    
    Raises:
        FileUploadException: Wenn der Upload fehlschlägt
    """
    try:
        # Dateiendung validieren
        validate_file_extension(file)
        
        # Dateigröße prüfen
        file_size = get_file_size(file)
        max_size = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
        
        if file_size > max_size:
            raise FileUploadException(
                f"Datei ist zu groß. Maximale Größe: {settings.MAX_UPLOAD_SIZE_MB}MB"
            )
        
        # Originaler Dateiname
        original_filename = file.filename or "unnamed"
        
        # Einzigartiger Dateiname
        unique_filename = generate_file_name(original_filename)
        
        # Zielpfad erstellen
        upload_dir = Path(settings.UPLOAD_DIR)
        if subdirectory:
            upload_dir = upload_dir / subdirectory
        
        os.makedirs(upload_dir, exist_ok=True)
        
        file_path = upload_dir / unique_filename
        
        # Datei speichern
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Datei-Informationen zurückgeben
        relative_path = str(file_path.relative_to(settings.UPLOAD_DIR))
        
        logger.info(f"Datei '{original_filename}' als '{unique_filename}' gespeichert")
        
        return (
            str(file_path),
            original_filename,
            file_size
        )
        
    except Exception as e:
        logger.error(f"Datei-Upload fehlgeschlagen: {e}")
        raise FileUploadException(str(e))


async def delete_file(file_path: str) -> bool:
    """
    Löscht eine Datei
    
    Args:
        file_path: Pfad zur Datei
    
    Returns:
        True wenn erfolgreich gelöscht
    """
    try:
        path = Path(file_path)
        if path.exists():
            path.unlink()
            logger.info(f"Datei '{file_path}' gelöscht")
            return True
        return False
    except Exception as e:
        logger.error(f"Datei-Löschung fehlgeschlagen: {e}")
        return False


def get_file_info(file_path: str) -> dict:
    """
    Gibt Informationen zu einer Datei zurück
    
    Args:
        file_path: Pfad zur Datei
    
    Returns:
        Dictionary mit Datei-Informationen
    """
    try:
        path = Path(file_path)
        if not path.exists():
            return {"exists": False}
        
        stat = path.stat()
        
        return {
            "exists": True,
            "path": str(file_path),
            "name": path.name,
            "size": stat.st_size,
            "size_mb": stat.st_size / (1024 * 1024),
            "modified": datetime.fromtimestamp(stat.st_mtime),
            "created": datetime.fromtimestamp(stat.st_ctime),
            "extension": path.suffix.lower()
        }
    except Exception as e:
        logger.error(f"Datei-Info Abruf fehlgeschlagen: {e}")
        return {"error": str(e)}
