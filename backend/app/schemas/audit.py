"""
Pydantic-Schemas für Audit-Log
"""

from pydantic import BaseModel, Field
from typing import Optional, Any, Dict
from datetime import datetime


class AuditLogResponse(BaseModel):
    """Response-Schema für Audit-Log-Einträge"""
    id: int
    uuid: str
    user_id: Optional[int] = None
    action: str
    table_name: str
    record_id: int
    old_values: Optional[Dict[str, Any]] = None
    new_values: Optional[Dict[str, Any]] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    created_at: datetime
    user: Optional[dict] = None
    changes: Dict[str, Any] = Field(default_factory=dict)
    changed_fields: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        from_attributes = True
