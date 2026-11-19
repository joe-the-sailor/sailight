"""
Authentifizierungs-API
JWT-basierte Authentifizierung mit OAuth2 Password Flow
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from datetime import datetime, timedelta
from typing import Optional
import logging

from app.config import settings
from app.database import get_db
from app.models.user import User
from app.schemas.user import UserLogin, TokenResponse
from app.utils.security import (
    create_access_token, create_refresh_token,
    verify_password, get_password_hash,
    get_current_user, get_current_active_user,
    oauth2_scheme
)
from app.utils.exceptions import (
    InvalidCredentialsException,
    InactiveUserException
)

router = APIRouter(prefix="/auth", tags=["Authentication"])
logger = logging.getLogger("sailight.auth")


@router.post("/token", response_model=TokenResponse, summary="Login und Token erhalten")
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """
    Erhält ein JWT-Token für authentifizierte Benutzer
    
    **Anmeldung:**
    - Benutzername und Passwort werden validiert
    - Bei Erfolg: access_token und refresh_token
    - access_token: 30 Minuten gültig
    - refresh_token: 7 Tage gültig
    """
    # Benutzer suchen
    result = await db.execute(
        select(User).where(User.username == form_data.username)
        .options(selectinload(User.roles))
    )
    user = result.scalar_one_or_none()
    
    if not user:
        logger.warning(f"Login fehlgeschlagen: Benutzer '{form_data.username}' nicht gefunden")
        raise InvalidCredentialsException()
    
    # Passwort prüfen
    if not verify_password(form_data.password, user.password_hash):
        logger.warning(f"Login fehlgeschlagen: Falsches Passwort für Benutzer '{form_data.username}'")
        raise InvalidCredentialsException()
    
    # Benutzer aktiv?
    if not user.is_active:
        logger.warning(f"Login fehlgeschlagen: Benutzer '{form_data.username}' ist inaktiv")
        raise InactiveUserException()
    
    # Token erstellen
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id), "username": user.username, "roles": user.role_names},
        expires_delta=access_token_expires
    )
    
    refresh_token_expires = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    refresh_token = create_refresh_token(
        data={"sub": str(user.id)},
        expires_delta=refresh_token_expires
    )
    
    # Letzter Login aktualisieren
    user.last_login = datetime.utcnow()
    await db.commit()
    await db.refresh(user)
    
    logger.info(f"Benutzer '{form_data.username}' erfolgreich angemeldet")
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user_id=user.id,
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        roles=user.role_names
    )


@router.post("/refresh", response_model=TokenResponse, summary="Token erneuern")
async def refresh_token(
    refresh_token: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Erneuert das access_token mit einem gültigen refresh_token
    """
    from jose import jwt, JWTError
    from app.utils.security import ALGORITHM, SECRET_KEY
    
    try:
        payload = jwt.decode(
            refresh_token, 
            SECRET_KEY, 
            algorithms=[ALGORITHM]
        )
        user_id: int = int(payload.get("sub"))
        
        # Benutzer suchen
        result = await db.execute(
            select(User).where(User.id == user_id)
            .options(selectinload(User.roles))
        )
        user = result.scalar_one_or_none()
        
        if not user or not user.is_active:
            raise InvalidCredentialsException()
        
        # Neues access_token erstellen
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": str(user.id), "username": user.username, "roles": user.role_names},
            expires_delta=access_token_expires
        )
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,  # Gleiches refresh_token zurückgeben
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user_id=user.id,
            username=user.username,
            email=user.email,
            full_name=user.full_name,
            roles=user.role_names
        )
        
    except JWTError as e:
        logger.error(f"Token-Erneuerung fehlgeschlagen: {e}")
        raise InvalidCredentialsException()


@router.post("/logout", summary="Logout")
async def logout(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """
    Beendet die Session (Token wird ungültig)
    
    **Hinweis:** JWT-Tokens sind stateless und können nicht direkt ungültig gemacht werden.
    In einer echten Implementierung würde man eine Blacklist verwenden.
    """
    logger.info(f"Benutzer '{current_user.username}' hat sich abgemeldet")
    return {"message": "Erfolgreich abgemeldet", "username": current_user.username}


@router.get("/me", summary="Aktueller Benutzer")
async def read_current_user(
    current_user: User = Depends(get_current_active_user)
):
    """
    Gibt die Informationen des aktuell angemeldeten Benutzers zurück
    """
    return {
        "id": current_user.id,
        "uuid": current_user.uuid,
        "username": current_user.username,
        "email": current_user.email,
        "first_name": current_user.first_name,
        "last_name": current_user.last_name,
        "full_name": current_user.full_name,
        "phone": current_user.phone,
        "department": current_user.department,
        "is_active": current_user.is_active,
        "last_login": current_user.last_login,
        "roles": current_user.role_names,
        "created_at": current_user.created_at
    }
