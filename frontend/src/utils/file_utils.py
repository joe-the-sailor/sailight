"""
Datei-Utilities für die Frontend-Anwendung
"""

import os
import shutil
from pathlib import Path
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger("sailight.file_utils")


def save_file(content: bytes, file_path: Path, overwrite: bool = False) -> bool:
    """
    Speichert eine Datei
    
    Args:
        content: Dateiinhalt
        file_path: Zielpfad
        overwrite: Überschreiben wenn vorhanden
    
    Returns:
        True wenn erfolgreich
    """
    try:
        # Verzeichnis erstellen
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Datei speichern
        if file_path.exists() and not overwrite:
            logger.warning(f"Datei existiert bereits: {file_path}")
            return False
        
        with open(file_path, "wb") as f:
            f.write(content)
        
        logger.info(f"Datei gespeichert: {file_path}")
        return True
        
    except Exception as e:
        logger.error(f"Fehler beim Speichern der Datei: {e}")
        return False


def open_file(file_path: Path) -> bool:
    """
    Öffnet eine Datei mit dem Standardprogramm
    
    Args:
        file_path: Pfad zur Datei
    
    Returns:
        True wenn erfolgreich
    """
    try:
        if not file_path.exists():
            logger.error(f"Datei nicht gefunden: {file_path}")
            return False
        
        # Plattform-spezifisches Öffnen
        if os.name == "nt":  # Windows
            os.startfile(str(file_path))
        elif os.name == "posix":  # Linux/Mac
            import subprocess
            subprocess.run(["xdg-open" if os.name == "posix" else "open", str(file_path)])
        
        logger.info(f"Datei geöffnet: {file_path}")
        return True
        
    except Exception as e:
        logger.error(f"Fehler beim Öffnen der Datei: {e}")
        return False


def get_file_info(file_path: Path) -> Dict[str, Any]:
    """
    Gibt Informationen zu einer Datei zurück
    
    Args:
        file_path: Pfad zur Datei
    
    Returns:
        Dictionary mit Datei-Informationen
    """
    try:
        if not file_path.exists():
            return {"exists": False}
        
        stat = file_path.stat()
        
        return {
            "exists": True,
            "path": str(file_path),
            "name": file_path.name,
            "size": stat.st_size,
            "size_formatted": format_bytes(stat.st_size),
            "modified": stat.st_mtime,
            "created": stat.st_ctime,
            "extension": file_path.suffix.lower()
        }
        
    except Exception as e:
        logger.error(f"Fehler beim Abrufen der Datei-Informationen: {e}")
        return {"error": str(e)}


def format_bytes(size: int) -> str:
    """
    Formatiert eine Dateigröße
    
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


def delete_file(file_path: Path) -> bool:
    """
    Löscht eine Datei
    
    Args:
        file_path: Pfad zur Datei
    
    Returns:
        True wenn erfolgreich
    """
    try:
        if file_path.exists():
            file_path.unlink()
            logger.info(f"Datei gelöscht: {file_path}")
            return True
        return False
        
    except Exception as e:
        logger.error(f"Fehler beim Löschen der Datei: {e}")
        return False


def copy_file(source: Path, destination: Path, overwrite: bool = False) -> bool:
    """
    Kopiert eine Datei
    
    Args:
        source: Quellenpfad
        destination: Zielpfad
        overwrite: Überschreiben wenn vorhanden
    
    Returns:
        True wenn erfolgreich
    """
    try:
        if not source.exists():
            logger.error(f"Quelldatei nicht gefunden: {source}")
            return False
        
        destination.parent.mkdir(parents=True, exist_ok=True)
        
        if destination.exists() and not overwrite:
            logger.warning(f"Zieldatei existiert bereits: {destination}")
            return False
        
        shutil.copy2(str(source), str(destination))
        logger.info(f"Datei kopiert: {source} -> {destination}")
        return True
        
    except Exception as e:
        logger.error(f"Fehler beim Kopieren der Datei: {e}")
        return False


def move_file(source: Path, destination: Path, overwrite: bool = False) -> bool:
    """
    Verschiebt eine Datei
    
    Args:
        source: Quellenpfad
        destination: Zielpfad
        overwrite: Überschreiben wenn vorhanden
    
    Returns:
        True wenn erfolgreich
    """
    try:
        if not source.exists():
            logger.error(f"Quelldatei nicht gefunden: {source}")
            return False
        
        destination.parent.mkdir(parents=True, exist_ok=True)
        
        if destination.exists() and not overwrite:
            logger.warning(f"Zieldatei existiert bereits: {destination}")
            return False
        
        shutil.move(str(source), str(destination))
        logger.info(f"Datei verschoben: {source} -> {destination}")
        return True
        
    except Exception as e:
        logger.error(f"Fehler beim Verschieben der Datei: {e}")
        return False
