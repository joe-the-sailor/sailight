"""
Konfiguration für die Sailight Frontend-Anwendung
"""

import os
from pathlib import Path
from typing import Optional
from dataclasses import dataclass


@dataclass
class Config:
    """Haupt-Konfiguration"""
    
    # Anwendung
    APP_NAME: str = "Sailight"
    APP_VERSION: str = "1.0.0"
    APP_TITLE: str = "Sailight - Straßenbeleuchtungsverwaltung"
    
    # API
    API_URL: str = os.getenv("FRONTEND_API_URL", "http://localhost:8000")
    API_V1_STR: str = "/api/v1"
    
    # GIS & Karten
    MAP_TILE_URL: str = os.getenv("MAP_TILE_URL", "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png")
    MAP_ATTRIBUTION: str = os.getenv(
        "MAP_ATTRIBUTION",
        '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    )
    GEOPORTAIL_URL: str = os.getenv("GEOPORTAIL_URL", "https://map.geoportail.lu/main")
    
    # Fenster-Einstellungen
    WINDOW_WIDTH: int = 1400
    WINDOW_HEIGHT: int = 900
    WINDOW_MIN_WIDTH: int = 1024
    WINDOW_MIN_HEIGHT: int = 768
    
    # Thema
    THEME: str = "dark"
    PRIMARY_COLOR: str = "#FF8C00"  # Dunkles Orange
    SECONDARY_COLOR: str = "#FF6B35"  # Helles Orange
    ACCENT_COLOR: str = "#FFA500"  # Orange
    BACKGROUND_COLOR: str = "#1E1E1E"  # Dunkles Grau
    SURFACE_COLOR: str = "#2D2D2D"  # Mittelgrau
    TEXT_COLOR: str = "#E0E0E0"  # Hellgrau
    TEXT_SECONDARY: str = "#A0A0A0"  # Grau
    BORDER_COLOR: str = "#404040"  # Dunkelgrau
    SUCCESS_COLOR: str = "#4CAF50"  # Grün
    WARNING_COLOR: str = "#FF9800"  # Orange
    ERROR_COLOR: str = "#F44336"  # Rot
    INFO_COLOR: str = "#2196F3"  # Blau
    
    # Tabellen
    TABLE_ROW_HEIGHT: int = 24
    TABLE_HEADER_HEIGHT: int = 30
    TABLE_ALTERNATE_COLOR: str = "#252525"
    
    # GIS
    GIS_DEFAULT_ZOOM: int = 13
    GIS_DEFAULT_CENTER: tuple = (6.1319, 49.6116)  # Luxemburg
    GIS_MIN_ZOOM: int = 6
    GIS_MAX_ZOOM: int = 19
    
    # Authentifizierung
    TOKEN_KEY: str = "sailight_token"
    REFRESH_TOKEN_KEY: str = "sailight_refresh_token"
    USER_KEY: str = "sailight_user"
    
    # Datei-Upload
    UPLOAD_DIR: Path = Path("uploads")
    MAX_UPLOAD_SIZE_MB: int = 100
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: Path = Path("logs/sailight_frontend.log")
    
    # Entwicklung
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"


# Instanz der Konfiguration
config = Config()

# Erstelle Verzeichnisse
os.makedirs(config.UPLOAD_DIR, exist_ok=True)
os.makedirs(config.LOG_FILE.parent, exist_ok=True)
