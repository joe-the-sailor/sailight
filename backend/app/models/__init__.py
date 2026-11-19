"""
SQLAlchemy-Modelle für Sailight
"""

from .geography import (
    Country, Region, Municipality, Street
)
from .user import User, Role, UserRole
from .infrastructure import (
    Cabinet, CircuitGroup, Pole, LightPoint
)
from .material import (
    MaterialCatalog, Lamp, LightPointMaterial, CabinetMaterial
)
from .energy import ElectricMeter, MeterReading, Invoice
from .maintenance import (
    IncidentType, IncidentStatus, Incident
)
from .project import (
    ProjectType, ProjectStatus, Project, ProjectInfrastructure
)
from .document import DocumentType, Document
from .audit import AuditLog

__all__ = [
    # Geografie
    'Country', 'Region', 'Municipality', 'Street',
    # Benutzer
    'User', 'Role', 'UserRole',
    # Infrastruktur
    'Cabinet', 'CircuitGroup', 'Pole', 'LightPoint',
    # Material
    'MaterialCatalog', 'Lamp', 'LightPointMaterial', 'CabinetMaterial',
    # Energie
    'ElectricMeter', 'MeterReading', 'Invoice',
    # Wartung
    'IncidentType', 'IncidentStatus', 'Incident',
    # Projekte
    'ProjectType', 'ProjectStatus', 'Project', 'ProjectInfrastructure',
    # Dokumente
    'DocumentType', 'Document',
    # Audit
    'AuditLog',
]
