"""
Authentifizierungs-Manager für die Frontend-Anwendung
"""

import json
import logging
from typing import Optional, Dict, Any
from pathlib import Path
from dataclasses import dataclass, field

from PyQt6.QtCore import QObject, pyqtSignal, QSettings
from frontend.src.config import config
from frontend.src.utils.api_client import APIClient, APIResponse

logger = logging.getLogger("sailight.auth")


@dataclass
class User:
    """Benutzer-Objekt"""
    id: int
    uuid: str
    username: str
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    full_name: str = ""
    phone: Optional[str] = None
    department: Optional[str] = None
    is_active: bool = True
    roles: list = field(default_factory=list)
    last_login: Optional[str] = None
    created_at: Optional[str] = None
    
    @property
    def display_name(self) -> str:
        """Anzeigename"""
        if self.full_name:
            return self.full_name
        return self.username
    
    def has_role(self, role: str) -> bool:
        """Prüft, ob der Benutzer eine bestimmte Rolle hat"""
        return role in self.roles
    
    def is_admin(self) -> bool:
        """Prüft, ob der Benutzer Admin ist"""
        return self.has_role("admin")
    
    def is_technician(self) -> bool:
        """Prüft, ob der Benutzer Techniker ist"""
        return self.has_role("technician")
    
    def is_clerk(self) -> bool:
        """Prüft, ob der Benutzer Sachbearbeiter ist"""
        return self.has_role("clerk")
    
    def to_dict(self) -> Dict[str, Any]:
        """Konvertiert zu Dictionary"""
        return {
            "id": self.id,
            "uuid": self.uuid,
            "username": self.username,
            "email": self.email,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "full_name": self.full_name,
            "phone": self.phone,
            "department": self.department,
            "is_active": self.is_active,
            "roles": self.roles,
            "last_login": self.last_login,
            "created_at": self.created_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "User":
        """Erstellt ein User-Objekt aus einem Dictionary"""
        return cls(
            id=data.get("id", 0),
            uuid=data.get("uuid", ""),
            username=data.get("username", ""),
            email=data.get("email", ""),
            first_name=data.get("first_name"),
            last_name=data.get("last_name"),
            full_name=data.get("full_name", ""),
            phone=data.get("phone"),
            department=data.get("department"),
            is_active=data.get("is_active", True),
            roles=data.get("roles", []),
            last_login=data.get("last_login"),
            created_at=data.get("created_at")
        )


@dataclass
class Token:
    """Token-Objekt"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = 0
    
    def is_expired(self) -> bool:
        """Prüft, ob das Token abgelaufen ist"""
        # Einfache Prüfung: Wenn expires_in 0 ist, nehmen wir an, es ist gültig
        return False


class AuthManager(QObject):
    """Authentifizierungs-Manager"""
    
    # Signale
    auth_state_changed = pyqtSignal(bool)  # True = authenticated, False = not authenticated
    user_changed = pyqtSignal(User)
    login_success = pyqtSignal(User)
    login_failed = pyqtSignal(str)
    logout_success = pyqtSignal()
    token_refreshed = pyqtSignal(Token)
    
    def __init__(self, api_client: Optional[APIClient] = None):
        """Initialisiert den Auth-Manager"""
        super().__init__()
        self._api_client = api_client or APIClient()
        self._user: Optional[User] = None
        self._token: Optional[Token] = None
        self._settings = QSettings("Sailight", "Frontend")
        
        # Token aus den Einstellungen laden
        self._load_tokens()
    
    def _load_tokens(self):
        """Lädt Token aus den Einstellungen"""
        access_token = self._settings.value(config.TOKEN_KEY, None)
        refresh_token = self._settings.value(config.REFRESH_TOKEN_KEY, None)
        
        if access_token and refresh_token:
            self._token = Token(
                access_token=access_token,
                refresh_token=refresh_token
            )
            self._api_client.set_token(access_token)
            # Benutzerdaten laden
            self._load_user()
    
    def _load_user(self):
        """Lädt Benutzerdaten aus den Einstellungen"""
        user_data = self._settings.value(config.USER_KEY, None)
        if user_data:
            self._user = User.from_dict(json.loads(user_data))
            self.auth_state_changed.emit(True)
            self.user_changed.emit(self._user)
    
    def _save_tokens(self, token: Token, user: User):
        """Speichert Token und Benutzer in den Einstellungen"""
        self._settings.setValue(config.TOKEN_KEY, token.access_token)
        self._settings.setValue(config.REFRESH_TOKEN_KEY, token.refresh_token)
        self._settings.setValue(config.USER_KEY, json.dumps(user.to_dict()))
        self._settings.sync()
    
    def _clear_tokens(self):
        """Löscht Token und Benutzer aus den Einstellungen"""
        self._settings.remove(config.TOKEN_KEY)
        self._settings.remove(config.REFRESH_TOKEN_KEY)
        self._settings.remove(config.USER_KEY)
        self._settings.sync()
    
    @property
    def is_authenticated(self) -> bool:
        """Prüft, ob der Benutzer authentifiziert ist"""
        return self._user is not None and self._token is not None
    
    @property
    def current_user(self) -> Optional[User]:
        """Gibt den aktuellen Benutzer zurück"""
        return self._user
    
    @property
    def current_token(self) -> Optional[Token]:
        """Gibt das aktuelle Token zurück"""
        return self._token
    
    async def login(self, username: str, password: str) -> bool:
        """
        Meldet einen Benutzer an
        
        Args:
            username: Benutzername
            password: Passwort
        
        Returns:
            True wenn erfolgreich, False sonst
        """
        try:
            # Token anfordern
            response = await self._api_client.post(
                f"{config.API_V1_STR}/auth/token",
                data={
                    "username": username,
                    "password": password,
                    "grant_type": "password"
                }
            )
            
            if response.success and response.data:
                # Token parsen
                token_data = response.data
                token = Token(
                    access_token=token_data.get("access_token", ""),
                    refresh_token=token_data.get("refresh_token", ""),
                    token_type=token_data.get("token_type", "bearer"),
                    expires_in=token_data.get("expires_in", 0)
                )
                
                # Benutzerdaten extrahieren
                user_data = {
                    "id": token_data.get("user_id", 0),
                    "uuid": "",
                    "username": token_data.get("username", ""),
                    "email": token_data.get("email", ""),
                    "full_name": token_data.get("full_name", ""),
                    "roles": token_data.get("roles", []),
                    "is_active": True
                }
                user = User.from_dict(user_data)
                
                # Token und Benutzer speichern
                self._token = token
                self._user = user
                self._api_client.set_token(token.access_token)
                self._save_tokens(token, user)
                
                # Signale auslösen
                self.auth_state_changed.emit(True)
                self.user_changed.emit(user)
                self.login_success.emit(user)
                
                logger.info(f"Benutzer '{username}' erfolgreich angemeldet")
                return True
            else:
                error_message = response.error or "Anmeldung fehlgeschlagen"
                self.login_failed.emit(error_message)
                logger.error(f"Anmeldung fehlgeschlagen: {error_message}")
                return False
                
        except Exception as e:
            self.login_failed.emit(str(e))
            logger.error(f"Anmeldung: Unerwarteter Fehler - {e}")
            return False
    
    async def logout(self) -> bool:
        """Meldet den aktuellen Benutzer ab"""
        try:
            # Logout-Request (optional)
            if self.is_authenticated:
                await self._api_client.post(f"{config.API_V1_STR}/auth/logout")
            
            # Lokale Daten löschen
            self._token = None
            self._user = None
            self._api_client.clear_token()
            self._clear_tokens()
            
            # Signale auslösen
            self.auth_state_changed.emit(False)
            self.logout_success.emit()
            
            logger.info("Benutzer erfolgreich abgemeldet")
            return True
            
        except Exception as e:
            logger.error(f"Logout: Fehler - {e}")
            # Trotzdem lokale Daten löschen
            self._token = None
            self._user = None
            self._api_client.clear_token()
            self._clear_tokens()
            self.auth_state_changed.emit(False)
            return False
    
    async def refresh_token(self) -> bool:
        """Erneuert das Access-Token"""
        if not self._token or not self._token.refresh_token:
            return False
        
        try:
            response = await self._api_client.post(
                f"{config.API_V1_STR}/auth/refresh",
                json={
                    "refresh_token": self._token.refresh_token
                }
            )
            
            if response.success and response.data:
                token_data = response.data
                new_token = Token(
                    access_token=token_data.get("access_token", self._token.access_token),
                    refresh_token=token_data.get("refresh_token", self._token.refresh_token),
                    token_type=token_data.get("token_type", self._token.token_type),
                    expires_in=token_data.get("expires_in", 0)
                )
                
                self._token = new_token
                self._api_client.set_token(new_token.access_token)
                self._save_tokens(new_token, self._user or User.from_dict({}))
                
                self.token_refreshed.emit(new_token)
                logger.info("Token erfolgreich erneuert")
                return True
            else:
                logger.error(f"Token-Erneuerung fehlgeschlagen: {response.error}")
                return False
                
        except Exception as e:
            logger.error(f"Token-Erneuerung: Fehler - {e}")
            return False
    
    async def get_current_user(self) -> Optional[User]:
        """Holt die aktuellen Benutzerdaten vom Server"""
        if not self.is_authenticated:
            return None
        
        try:
            response = await self._api_client.get(f"{config.API_V1_STR}/auth/me")
            
            if response.success and response.data:
                user_data = response.data
                self._user = User.from_dict(user_data)
                self.user_changed.emit(self._user)
                return self._user
            else:
                logger.error(f"Benutzerdaten abrufen: {response.error}")
                return None
                
        except Exception as e:
            logger.error(f"Benutzerdaten abrufen: Fehler - {e}")
            return None


# Globale Instanz
auth_manager = AuthManager()
