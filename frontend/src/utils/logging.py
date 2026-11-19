"""
Logging-Konfiguration für die Frontend-Anwendung
"""

import logging
import logging.handlers
from pathlib import Path
from typing import Optional
import sys


def setup_logging(
    level: str = "INFO",
    log_file: Optional[Path] = None,
    console: bool = True
):
    """
    Richtet das Logging ein
    
    Args:
        level: Log-Level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Pfad zur Log-Datei
        console: Log auf Konsole ausgeben
    """
    # Log-Level parsen
    log_level = getattr(logging, level.upper(), logging.INFO)
    
    # Root-Logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Bestehende Handler entfernen
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Format
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    # Console-Handler
    if console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(log_level)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)
    
    # File-Handler
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.handlers.RotatingFileHandler(
            str(log_file),
            maxBytes=10 * 1024 * 1024,  # 10 MB
            backupCount=5,
            encoding="utf-8"
        )
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    
    # Sailight-Logger
    sailight_logger = logging.getLogger("sailight")
    sailight_logger.setLevel(log_level)


def get_logger(name: str) -> logging.Logger:
    """
    Gibt einen Logger für ein bestimmtes Modul zurück
    
    Args:
        name: Modulname
    
    Returns:
        Logger-Instanz
    """
    return logging.getLogger(f"sailight.{name}")


# Standard-Logging einrichten
setup_logging("INFO", Path("logs/sailight_frontend.log"))
