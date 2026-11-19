"""
Konfiguration für die Sailight Backend-Anwendung
"""

from pydantic_settings import BaseSettings
from pydantic import Field, PostgresDsn, RedisDsn
from typing import List, Optional
import os
from pathlib import Path


class Settings(BaseSettings):
    """Haupt-Konfiguration"""
    
    # Anwendung
    APP_NAME: str = "Sailight API"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = "Straßenbeleuchtungsverwaltung für Administration des Ponts et Chaussées"
    DEBUG: bool = Field(default=False, env="DEBUG")
    
    # API
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = Field(default="sailight-secret-key-change-in-production", env="SECRET_KEY")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # CORS
    CORS_ORIGINS: List[str] = Field(
        default=["*"],
        env="CORS_ORIGINS"
    )
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: List[str] = ["*"]
    CORS_ALLOW_HEADERS: List[str] = ["*"]
    
    # Datenbank
    DATABASE_URL: PostgresDsn = Field(
        default="postgresql+asyncpg://sailight_user:sailight_pass_2024@localhost:5432/sailight",
        env="DATABASE_URL"
    )
    DATABASE_TEST_URL: Optional[PostgresDsn] = Field(
        default=None,
        env="DATABASE_TEST_URL"
    )
    
    # Redis
    REDIS_URL: RedisDsn = Field(
        default="redis://localhost:6379/0",
        env="REDIS_URL"
    )
    
    # Celery
    CELERY_BROKER_URL: str = Field(
        default="redis://localhost:6379/1",
        env="CELERY_BROKER_URL"
    )
    CELERY_RESULT_BACKEND: str = Field(
        default="redis://localhost:6379/2",
        env="CELERY_RESULT_BACKEND"
    )
    
    # GIS & Karten
    MAP_TILE_URL: str = Field(
        default="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
        env="MAP_TILE_URL"
    )
    MAP_ATTRIBUTION: str = Field(
        default='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
        env="MAP_ATTRIBUTION"
    )
    GEOPORTAIL_URL: str = Field(
        default="https://map.geoportail.lu/main",
        env="GEOPORTAIL_URL"
    )
    
    # Datei-Upload
    UPLOAD_DIR: Path = Field(
        default=Path("./uploads"),
        env="UPLOAD_DIR"
    )
    MAX_UPLOAD_SIZE_MB: int = 100
    ALLOWED_EXTENSIONS: List[str] = [
        ".pdf", ".jpg", ".jpeg", ".png", ".gif", 
        ".dwg", ".dxf", ".zip", ".docx", ".xlsx"
    ]
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: Path = Path("./logs/sailight.log")
    
    class Config:
        case_sensitive = True
        env_file = ".env"
        env_file_encoding = "utf-8"


# Instanz der Einstellungen
settings = Settings()

# Erstelle Upload-Verzeichnis wenn nicht vorhanden
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(settings.LOG_FILE.parent, exist_ok=True)
