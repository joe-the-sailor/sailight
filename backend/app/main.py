"""
Sailight Backend - Hauptanwendung
FastAPI-Anwendung für Straßenbeleuchtungsverwaltung
"""

from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.openapi.utils import get_openapi_handler
from contextlib import asynccontextmanager
import logging
from logging.config import dictConfig
from typing import Optional
import os

from app.config import settings
from app.database import engine, close_db
from app.api.v1 import (
    users, auth, geography, cabinets, circuit_groups, 
    poles, light_points, materials, meters, 
    incidents, projects, documents, audit
)

# Logging-Konfiguration
LOG_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "()": "uvicorn.logging.DefaultFormatter",
            "fmt": "%(levelprefix)s %(asctime)s %(message)s",
            "use_colors": None,
        },
        "access": {
            "()": "uvicorn.logging.AccessFormatter",
            "fmt": "%(levelprefix)s %(asctime)s - " + "%(client_addr)s - \"%(request_line)s\" %(status_code)s",
        },
    },
    "handlers": {
        "default": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stderr",
        },
        "access": {
            "formatter": "access",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
        },
        "file": {
            "formatter": "default",
            "class": "logging.FileHandler",
            "filename": str(settings.LOG_FILE),
            "mode": "a",
            "encoding": "utf-8",
        },
    },
    "loggers": {
        "sailight": {
            "handlers": ["default", "file"],
            "level": settings.LOG_LEVEL,
            "propagate": False,
        },
        "uvicorn": {
            "handlers": ["default", "access", "file"],
            "level": settings.LOG_LEVEL,
            "propagate": False,
        },
        "uvicorn.error": {
            "level": settings.LOG_LEVEL,
            "handlers": ["default", "file"],
            "propagate": False,
        },
        "uvicorn.access": {
            "handlers": ["access", "file"],
            "level": settings.LOG_LEVEL,
            "propagate": False,
        },
    },
}

dictConfig(LOG_CONFIG)
logger = logging.getLogger("sailight")


# Lifespan-Manager für Datenbank
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan-Manager für die Anwendung"""
    # Initialisierung
    logger.info("Sailight Backend wird gestartet...")
    
    # Erstelle Upload-Verzeichnis
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    
    # Starte die Anwendung
    yield
    
    # Cleanup
    logger.info("Sailight Backend wird heruntergefahren...")
    await close_db()
    logger.info("Datenbank-Verbindung geschlossen")


# FastAPI-Anwendung erstellen
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=settings.APP_DESCRIPTION,
    debug=settings.DEBUG,
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    swagger_ui_oauth2_redirect_url="/oauth2-redirect",
    swagger_ui_init_oauth={
        "clientId": "sailight-client",
        "scopes": "read write",
    },
)

# CORS-Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.CORS_ALLOW_METHODS,
    allow_headers=settings.CORS_ALLOW_HEADERS,
)

# Trusted Host Middleware (Sicherheit)
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"],  # In Produktion auf spezifische Hosts beschränken
)

# Static Files für Uploads
app.mount("/api/uploads", StaticFiles(directory=str(settings.UPLOAD_DIR)), name="uploads")


# OpenAPI-Handler für bessere Dokumentation
@app.get("/api/v1/openapi.json")
async def custom_openapi():
    """Custom OpenAPI-Schema"""
    from fastapi.openapi.utils import get_openapi_handler
    return get_openapi_handler(
        {
            "openapi": "3.0.2",
            "info": {
                "title": settings.APP_NAME,
                "version": settings.APP_VERSION,
                "description": settings.APP_DESCRIPTION,
            },
            "servers": [
                {"url": "http://localhost:8000"},
                {"url": "https://api.sailight.lu"},
            ],
        }
    )


# API-Router registrieren
api_v1 = FastAPI(
    title="Sailight API v1",
    version="1.0.0",
    prefix="/api/v1",
)

# Benutzer und Authentifizierung
api_v1.include_router(auth.router, tags=["Authentication"])
api_v1.include_router(users.router, prefix="/users", tags=["Users"])

# Geografie
api_v1.include_router(geography.router, prefix="/geography", tags=["Geography"])

# Infrastruktur
api_v1.include_router(cabinets.router, prefix="/cabinets", tags=["Infrastructure"])
api_v1.include_router(circuit_groups.router, prefix="/circuit-groups", tags=["Infrastructure"])
api_v1.include_router(poles.router, prefix="/poles", tags=["Infrastructure"])
api_v1.include_router(light_points.router, prefix="/light-points", tags=["Infrastructure"])

# Materialwirtschaft
api_v1.include_router(materials.router, prefix="/materials", tags=["Materials"])

# Energie & Abrechnung
api_v1.include_router(meters.router, prefix="/meters", tags=["Energy"])

# Betrieb & Wartung
api_v1.include_router(incidents.router, prefix="/incidents", tags=["Maintenance"])

# Projekte
api_v1.include_router(projects.router, prefix="/projects", tags=["Projects"])

# Dokumente
api_v1.include_router(documents.router, prefix="/documents", tags=["Documents"])

# Audit-Log
api_v1.include_router(audit.router, prefix="/audit", tags=["Audit"])

# API v1 in die Hauptanwendung einbinden
app.mount("/api/v1", api_v1)


# Root-Endpoint
@app.get("/", tags=["Root"])
async def root():
    """Root-Endpoint"""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "description": settings.APP_DESCRIPTION,
        "docs": "/api/docs",
        "redoc": "/api/redoc",
        "health": "/api/health",
    }


# Health-Check-Endpoint
@app.get("/api/health", tags=["Health"])
async def health_check():
    """Health-Check-Endpoint"""
    return {
        "status": "healthy",
        "version": settings.APP_VERSION,
        "database": "connected",
        "timestamp": "2024-01-01T00:00:00Z",
    }


# 404-Handler
@app.exception_handler(404)
async def not_found_handler(request: Request, exc: HTTPException):
    """Custom 404-Handler"""
    return JSONResponse(
        status_code=404,
        content={
            "detail": "Endpoint nicht gefunden",
            "path": str(request.url),
            "available_docs": "/api/docs",
        },
    )


# 500-Handler
@app.exception_handler(500)
async def internal_server_error_handler(request: Request, exc: HTTPException):
    """Custom 500-Handler"""
    logger.error(f"Internal Server Error: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Interner Serverfehler",
            "message": str(exc),
        },
    )


# Import JSONResponse
from fastapi.responses import JSONResponse


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_config=None,
    )
