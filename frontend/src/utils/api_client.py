"""
API-Client für die Kommunikation mit dem Backend
"""

import httpx
import json
import logging
from typing import Optional, Dict, Any, Union, List
from dataclasses import dataclass
from pathlib import Path

from frontend.src.config import config

logger = logging.getLogger("sailight.api_client")


@dataclass
class APIResponse:
    """API-Response-Objekt"""
    data: Any
    status_code: int
    success: bool
    message: Optional[str] = None
    error: Optional[str] = None


class APIClient:
    """HTTP-Client für die API-Kommunikation"""
    
    def __init__(self, base_url: Optional[str] = None, timeout: float = 30.0):
        """
        Initialisiert den API-Client
        
        Args:
            base_url: Basis-URL der API
            timeout: Timeout in Sekunden
        """
        self.base_url = base_url or config.API_URL
        self.timeout = timeout
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=self.timeout,
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
        )
        self._token: Optional[str] = None
    
    def set_token(self, token: str):
        """Setzt das Authentifizierungs-Token"""
        self._token = token
        self._client.headers["Authorization"] = f"Bearer {token}"
    
    def clear_token(self):
        """Löscht das Authentifizierungs-Token"""
        self._token = None
        if "Authorization" in self._client.headers:
            del self._client.headers["Authorization"]
    
    async def __aenter__(self):
        """Async Context Manager - Enter"""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async Context Manager - Exit"""
        await self.close()
    
    async def close(self):
        """Schließt die Verbindung"""
        await self._client.aclose()
    
    async def _request(
        self,
        method: str,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> APIResponse:
        """
        Führt eine HTTP-Anfrage aus
        
        Args:
            method: HTTP-Methode (GET, POST, PUT, DELETE, etc.)
            url: URL (relativ zur Basis-URL)
            params: Query-Parameter
            data: Form-Daten
            json: JSON-Daten
            files: Dateien für Upload
            headers: Zusätzliche Header
        
        Returns:
            APIResponse-Objekt
        """
        try:
            # Header kombinieren
            request_headers = {**(self._client.headers or {}), **(headers or {})}
            
            # Anfrage ausführen
            response = await self._client.request(
                method,
                url,
                params=params,
                data=data,
                json=json,
                files=files,
                headers=request_headers
            )
            
            # Response verarbeiten
            try:
                response_data = response.json()
            except (json.JSONDecodeError, ValueError):
                response_data = None
            
            # Erfolg prüfen
            if response.is_success:
                return APIResponse(
                    data=response_data,
                    status_code=response.status_code,
                    success=True
                )
            else:
                error_message = response_data.get("detail", "Unbekannter Fehler") if response_data else response.text
                return APIResponse(
                    data=response_data,
                    status_code=response.status_code,
                    success=False,
                    error=error_message
                )
                
        except httpx.TimeoutException:
            logger.error("API-Anfrage: Timeout")
            return APIResponse(
                data=None,
                status_code=504,
                success=False,
                error="Timeout: Die Anfrage hat zu lange gedauert"
            )
        except httpx.ConnectError:
            logger.error("API-Anfrage: Verbindung fehlgeschlagen")
            return APIResponse(
                data=None,
                status_code=502,
                success=False,
                error="Verbindung fehlgeschlagen: Server nicht erreichbar"
            )
        except httpx.RequestError as e:
            logger.error(f"API-Anfrage: Fehler - {e}")
            return APIResponse(
                data=None,
                status_code=500,
                success=False,
                error=f"Anfragefehler: {str(e)}"
            )
        except Exception as e:
            logger.error(f"API-Anfrage: Unerwarteter Fehler - {e}")
            return APIResponse(
                data=None,
                status_code=500,
                success=False,
                error=f"Unerwarteter Fehler: {str(e)}"
            )
    
    # Convenience-Methoden
    
    async def get(
        self,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> APIResponse:
        """GET-Anfrage"""
        return await self._request("GET", url, params=params, headers=headers)
    
    async def post(
        self,
        url: str,
        json: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> APIResponse:
        """POST-Anfrage"""
        return await self._request("POST", url, json=json, data=data, files=files, headers=headers)
    
    async def put(
        self,
        url: str,
        json: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> APIResponse:
        """PUT-Anfrage"""
        return await self._request("PUT", url, json=json, data=data, headers=headers)
    
    async def patch(
        self,
        url: str,
        json: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> APIResponse:
        """PATCH-Anfrage"""
        return await self._request("PATCH", url, json=json, data=data, headers=headers)
    
    async def delete(
        self,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> APIResponse:
        """DELETE-Anfrage"""
        return await self._request("DELETE", url, params=params, headers=headers)


# Globale Instanz
api_client = APIClient()
