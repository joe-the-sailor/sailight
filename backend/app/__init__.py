"""
Sailight Backend - FastAPI Application
Straßenbeleuchtungsverwaltung für Administration des Ponts et Chaussées, Luxemburg
"""

__version__ = "1.0.0"
__author__ = "Joe the Sailor"
__description__ = "Professionelle Straßenbeleuchtungsverwaltung mit GIS-Integration"

# Import Celery app for background tasks
from app.celery_app import celery_app
from app import tasks
