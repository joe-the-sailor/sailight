"""
Sicherheits-Utilities: JWT, Passwort-Hashing, Authentifizierung
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
import logging

from app.config import settings
from app.database import get_db
from app.models.user import User
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

logger = logging.getLogger("sailight.security")

# Passwort-Hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT-Konfiguration
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM

# OAuth2-Schema
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/token",
    scopes={"read": "Lesen", "write": "Schreiben", "admin": "Administrator"}
)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Überprüft ein Passwort gegen einen Hash"""
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception as e:
        logger.error(f"Passwort-Überprüfung fehlgeschlagen: {e}")
        return False


def get_password_hash(password: str) -> str:
    """Erzeugt einen Hash für ein Passwort"""
    return pwd_context.hash(password)


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Erstellt ein JWT access_token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "access_token"
    })
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Erstellt ein JWT refresh_token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=7)
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "refresh_token"
    })
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> Dict[str, Any]:
    """Dekodiert ein JWT-Token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError as e:
        logger.error(f"Token-Dekodierung fehlgeschlagen: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Ungültiges Token",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    """Holt den aktuellen Benutzer aus dem Token"""
    try:
        payload = decode_token(token)
        user_id: int = int(payload.get("sub"))
        
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Ungültiges Token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Benutzer aus der Datenbank laden
        result = await db.execute(
            select(User).where(User.id == user_id)
            .options(selectinload(User.roles))
        )
        user = result.scalar_one_or_none()
        
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Benutzer nicht gefunden",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return user
        
    except JWTError as e:
        logger.error(f"Authentifizierung fehlgeschlagen: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Ungültiges Token",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Holt den aktuellen aktiven Benutzer"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inaktiver Benutzer"
        )
    return current_user


async def get_current_user_with_roles(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """Holt den aktuellen Benutzer mit geladenen Rollen"""
    # Rollen sind bereits durch selectinload geladen
    return current_user


def has_role(user: User, role_name: str) -> bool:
    """Prüft, ob der Benutzer eine bestimmte Rolle hat"""
    return user.has_role(role_name)


def has_any_role(user: User, role_names: list) -> bool:
    """Prüft, ob der Benutzer eine der Rollen hat"""
    return any(has_role(user, role) for role in role_names)


class RoleChecker:
    """Hilfsklasse für Rollenprüfungen"""
    
    def __init__(self, allowed_roles: list):
        self.allowed_roles = allowed_roles
    
    def __call__(self, user: User = Depends(get_current_active_user)):
        if not has_any_role(user, self.allowed_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Keine Berechtigung für diese Aktion"
            )
        return user


# Rollen-Checker für häufige Rollen
require_admin = RoleChecker(["admin"])
require_technician = RoleChecker(["admin", "technician"])
require_clerk = RoleChecker(["admin", "clerk"])
require_user = RoleChecker(["admin", "technician", "clerk"])
