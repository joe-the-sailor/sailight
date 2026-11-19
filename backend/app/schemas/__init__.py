"""
Pydantic-Schemas für Request/Response-Validierung
"""

from .user import (
    UserCreate, UserUpdate, UserResponse, UserLogin, 
    TokenResponse, RoleCreate, RoleUpdate, RoleResponse
)
from .geography import (
    CountryCreate, CountryUpdate, CountryResponse,
    RegionCreate, RegionUpdate, RegionResponse,
    MunicipalityCreate, MunicipalityUpdate, MunicipalityResponse,
    StreetCreate, StreetUpdate, StreetResponse
)
from .infrastructure import (
    CabinetCreate, CabinetUpdate, CabinetResponse,
    CircuitGroupCreate, CircuitGroupUpdate, CircuitGroupResponse,
    PoleCreate, PoleUpdate, PoleResponse,
    LightPointCreate, LightPointUpdate, LightPointResponse
)
from .material import (
    MaterialCatalogCreate, MaterialCatalogUpdate, MaterialCatalogResponse,
    LampCreate, LampUpdate, LampResponse
)
from .energy import (
    ElectricMeterCreate, ElectricMeterUpdate, ElectricMeterResponse,
    MeterReadingCreate, MeterReadingUpdate, MeterReadingResponse,
    InvoiceCreate, InvoiceUpdate, InvoiceResponse
)
from .maintenance import (
    IncidentTypeCreate, IncidentTypeUpdate, IncidentTypeResponse,
    IncidentStatusCreate, IncidentStatusUpdate, IncidentStatusResponse,
    IncidentCreate, IncidentUpdate, IncidentResponse
)
from .project import (
    ProjectTypeCreate, ProjectTypeUpdate, ProjectTypeResponse,
    ProjectStatusCreate, ProjectStatusUpdate, ProjectStatusResponse,
    ProjectCreate, ProjectUpdate, ProjectResponse,
    ProjectInfrastructureCreate, ProjectInfrastructureUpdate, ProjectInfrastructureResponse
)
from .document import (
    DocumentTypeCreate, DocumentTypeUpdate, DocumentTypeResponse,
    DocumentCreate, DocumentUpdate, DocumentResponse
)
from .audit import AuditLogResponse
from .common import (
    PaginatedResponse, FilterParams, SortParams, MessageResponse
)

__all__ = [
    # Common
    'PaginatedResponse', 'FilterParams', 'SortParams', 'MessageResponse',
    # User
    'UserCreate', 'UserUpdate', 'UserResponse', 'UserLogin',
    'TokenResponse', 'RoleCreate', 'RoleUpdate', 'RoleResponse',
    # Geography
    'CountryCreate', 'CountryUpdate', 'CountryResponse',
    'RegionCreate', 'RegionUpdate', 'RegionResponse',
    'MunicipalityCreate', 'MunicipalityUpdate', 'MunicipalityResponse',
    'StreetCreate', 'StreetUpdate', 'StreetResponse',
    # Infrastructure
    'CabinetCreate', 'CabinetUpdate', 'CabinetResponse',
    'CircuitGroupCreate', 'CircuitGroupUpdate', 'CircuitGroupResponse',
    'PoleCreate', 'PoleUpdate', 'PoleResponse',
    'LightPointCreate', 'LightPointUpdate', 'LightPointResponse',
    # Material
    'MaterialCatalogCreate', 'MaterialCatalogUpdate', 'MaterialCatalogResponse',
    'LampCreate', 'LampUpdate', 'LampResponse',
    # Energy
    'ElectricMeterCreate', 'ElectricMeterUpdate', 'ElectricMeterResponse',
    'MeterReadingCreate', 'MeterReadingUpdate', 'MeterReadingResponse',
    'InvoiceCreate', 'InvoiceUpdate', 'InvoiceResponse',
    # Maintenance
    'IncidentTypeCreate', 'IncidentTypeUpdate', 'IncidentTypeResponse',
    'IncidentStatusCreate', 'IncidentStatusUpdate', 'IncidentStatusResponse',
    'IncidentCreate', 'IncidentUpdate', 'IncidentResponse',
    # Project
    'ProjectTypeCreate', 'ProjectTypeUpdate', 'ProjectTypeResponse',
    'ProjectStatusCreate', 'ProjectStatusUpdate', 'ProjectStatusResponse',
    'ProjectCreate', 'ProjectUpdate', 'ProjectResponse',
    'ProjectInfrastructureCreate', 'ProjectInfrastructureUpdate', 'ProjectInfrastructureResponse',
    # Document
    'DocumentTypeCreate', 'DocumentTypeUpdate', 'DocumentTypeResponse',
    'DocumentCreate', 'DocumentUpdate', 'DocumentResponse',
    # Audit
    'AuditLogResponse',
]
