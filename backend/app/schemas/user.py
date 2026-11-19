"""
Pydantic-Schemas für Benutzer und Rollen
"""

from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional
from datetime import datetime


class TokenResponse(BaseModel):
    """Response für JWT-Token"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user_id: int
    username: str
    email: str
    full_name: str
    roles: List[str]


class RoleBase(BaseModel):
    """Basis-Schema für Rollen"""
    name: str = Field(..., min_length=1, max_length=50, description="Rollenname")
    description: Optional[str] = Field(default=None, description="Beschreibung")
    is_active: bool = Field(default=True, description="Ist die Rolle aktiv?")


class RoleCreate(RoleBase):
    """Schema zum Erstellen einer Rolle"""
    pass


class RoleUpdate(BaseModel):
    """Schema zum Aktualisieren einer Rolle"""
    name: Optional[str] = Field(default=None, min_length=1, max_length=50)
    description: Optional[str] = Field(default=None)
    is_active: Optional[bool] = Field(default=None)


class RoleResponse(RoleBase):
    """Response-Schema für Rollen"""
    id: int
    uuid: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class UserBase(BaseModel):
    """Basis-Schema für Benutzer"""
    username: str = Field(..., min_length=3, max_length=50, description="Benutzername")
    email: EmailStr = Field(..., description="E-Mail-Adresse")
    first_name: Optional[str] = Field(default=None, max_length=100, description="Vorname")
    last_name: Optional[str] = Field(default=None, max_length=100, description="Nachname")
    phone: Optional[str] = Field(default=None, max_length=20, description="Telefonnummer")
    department: Optional[str] = Field(default=None, max_length=100, description="Abteilung")


class UserCreate(UserBase):
    """Schema zum Erstellen eines Benutzers"""
    password: str = Field(..., min_length=8, description="Passwort (mind. 8 Zeichen)")
    is_active: bool = Field(default=True, description="Ist der Benutzer aktiv?")
    role_ids: List[int] = Field(default_factory=list, description="Rollen-IDs")


class UserUpdate(BaseModel):
    """Schema zum Aktualisieren eines Benutzers"""
    username: Optional[str] = Field(default=None, min_length=3, max_length=50)
    email: Optional[EmailStr] = Field(default=None)
    first_name: Optional[str] = Field(default=None, max_length=100)
    last_name: Optional[str] = Field(default=None, max_length=100)
    phone: Optional[str] = Field(default=None, max_length=20)
    department: Optional[str] = Field(default=None, max_length=100)
    is_active: Optional[bool] = Field(default=None)
    password: Optional[str] = Field(default=None, min_length=8)
    role_ids: Optional[List[int]] = Field(default=None)


class UserLogin(BaseModel):
    """Schema für Login"""
    username: str = Field(..., description="Benutzername")
    password: str = Field(..., description="Passwort")


class UserResponse(UserBase):
    """Response-Schema für Benutzer"""
    id: int
    uuid: str
    is_active: bool
    last_login: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    roles: List[RoleResponse] = Field(default_factory=list)
    
    class Config:
        from_attributes = True


class UserListResponse(BaseModel):
    """Schema für Benutzer-Liste"""
    id: int
    uuid: str
    username: str
    email: str
    full_name: str
    is_active: bool
    roles: List[str] = Field(default_factory=list)
    created_at: datetime
    
    class Config:
        from_attributes = True
