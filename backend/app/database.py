"""
Datenbank-Konfiguration und Session-Management
"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_scoped_session
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.ext.declarative import DeclarativeMeta
from geoalchemy2 import Geometry
from geoalchemy2.types import GeometryType
from typing import Optional, Any
import asyncio
from contextlib import asynccontextmanager

from app.config import settings


# SQLAlchemy Base mit GeoAlchemy2-Unterstützung
class Base(declarative_base()):
    """Basis-Klasse für alle SQLAlchemy-Modelle"""
    pass


# Asynchroner Datenbank-Engine
engine = create_async_engine(
    str(settings.DATABASE_URL),
    echo=settings.DEBUG,
    future=True,
    pool_pre_ping=True,
    pool_size=20,
    max_overflow=10,
)

# Asynchrone Session-Factory
async_session_factory = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Scoped Session für Request-Kontext
async_scoped_session = async_scoped_session(
    async_session_factory,
    scopefunc=asyncio.current_task
)


# Typ-Hinweis für SQLAlchemy-Modelle
ModelType = DeclarativeMeta


async def get_db() -> AsyncSession:
    """
    Dependency Injection für Datenbank-Sessions
    """
    async with async_scoped_session() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            raise e
        finally:
            await session.close()


@asynccontextmanager
async def get_db_context():
    """
    Kontext-Manager für Datenbank-Sessions
    """
    async with async_scoped_session() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            raise e
        finally:
            await session.close()


async def init_db():
    """
    Initialisiert die Datenbank (erstellt Tabellen)
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        print("Datenbank-Tabellen wurden erstellt/überprüft")


async def close_db():
    """
    Schließt die Datenbank-Verbindung
    """
    await engine.dispose()
    print("Datenbank-Verbindung geschlossen")


# Geometry-Type für SQLAlchemy
# Dies ermöglicht die Verwendung von PostGIS-Geometrien in den Modellen
class GeometryColumn:
    """Hilfsklasse für Geometry-Spalten"""
    
    @staticmethod
    def geometry(srid: int = 4326, dimension: int = 2) -> Any:
        """Erstellt eine Geometry-Spalte mit SRID"""
        return Geometry(
            geometry_type=GeometryType("GEOMETRY", srid=srid),
            spatial_index=True
        )
    
    @staticmethod
    def point(srid: int = 4326) -> Any:
        """Erstellt eine Point-Spalte"""
        return Geometry(
            geometry_type=GeometryType("POINT", srid=srid),
            spatial_index=True
        )
    
    @staticmethod
    def linestring(srid: int = 4326) -> Any:
        """Erstellt eine LineString-Spalte"""
        return Geometry(
            geometry_type=GeometryType("LINESTRING", srid=srid),
            spatial_index=True
        )
    
    @staticmethod
    def polygon(srid: int = 4326) -> Any:
        """Erstellt eine Polygon-Spalte"""
        return Geometry(
            geometry_type=GeometryType("POLYGON", srid=srid),
            spatial_index=True
        )
