"""
Custom Exceptions für Sailight
"""

from fastapi import HTTPException, status
from typing import Any, Dict, Optional
import logging

logger = logging.getLogger("sailight.exceptions")


class SailightException(HTTPException):
    """Basis-Exception für Sailight"""
    
    def __init__(
        self,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail: str = "Ein Fehler ist aufgetreten",
        headers: Optional[Dict[str, Any]] = None
    ):
        super().__init__(status_code=status_code, detail=detail, headers=headers)
        logger.error(f"SailightException: {status_code} - {detail}")


class NotFoundException(SailightException):
    """Ressource nicht gefunden"""
    
    def __init__(self, resource: str = "Ressource", resource_id: Optional[int] = None):
        if resource_id:
            detail = f"{resource} mit ID {resource_id} nicht gefunden"
        else:
            detail = f"{resource} nicht gefunden"
        
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail
        )


class InvalidCredentialsException(SailightException):
    """Ungültige Anmeldedaten"""
    
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Ungültige Anmeldedaten",
            headers={"WWW-Authenticate": "Bearer"}
        )


class InactiveUserException(SailightException):
    """Inaktiver Benutzer"""
    
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Benutzer ist inaktiv"
        )


class PermissionDeniedException(SailightException):
    """Keine Berechtigung"""
    
    def __init__(self, detail: str = "Keine Berechtigung für diese Aktion"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail
        )


class ValidationException(SailightException):
    """Validierungsfehler"""
    
    def __init__(self, detail: str = "Validierungsfehler"):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail
        )


class DuplicateEntryException(SailightException):
    """Doppelte Einträge"""
    
    def __init__(self, field: str, value: Any):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{field} '{value}' existiert bereits"
        )


class FileUploadException(SailightException):
    """Datei-Upload-Fehler"""
    
    def __init__(self, detail: str = "Datei-Upload fehlgeschlagen"):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail
        )


class GISException(SailightException):
    """GIS-Fehler"""
    
    def __init__(self, detail: str = "GIS-Operation fehlgeschlagen"):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail
        )
