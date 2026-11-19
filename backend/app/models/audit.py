"""
Audit-Log-Modell für Änderungen-Protokollierung
"""

from sqlalchemy import Column, BIGINT, Integer, String, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from typing import Optional, Any, Dict
from datetime import datetime

from app.database import Base


class ActionType(str):
    """Aktions-Typen für Audit-Log"""
    CREATE = "CREATE"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    LOGIN = "LOGIN"
    LOGOUT = "LOGOUT"


class AuditLog(Base):
    """Audit-Log für alle Änderungen"""
    __tablename__ = "audit_log"
    
    id = Column(BIGINT, primary_key=True, index=True)
    uuid = Column(String(36), unique=True, index=True)
    user_id = Column(Integer, ForeignKey("user_table.id", ondelete="SET NULL"), index=True)
    action = Column(String(50), nullable=False, index=True)
    table_name = Column(String(50), nullable=False, index=True)
    record_id = Column(Integer, nullable=False, index=True)
    old_values = Column(JSON)
    new_values = Column(JSON)
    ip_address = Column(String(45))
    user_agent = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Beziehungen
    user: Optional["User"] = relationship("User", foreign_keys=[user_id], back_populates="audit_logs")
    
    def __repr__(self):
        return f"<AuditLog(id={self.id}, action='{self.action}', table='{self.table_name}', record_id={self.record_id})>"
    
    @property
    def changes(self) -> Dict[str, Any]:
        """Gibt die Änderungen als Dictionary zurück"""
        changes = {}
        if self.old_values:
            changes["old"] = self.old_values
        if self.new_values:
            changes["new"] = self.new_values
        return changes
    
    @property
    def changed_fields(self) -> Dict[str, Any]:
        """Gibt nur die geänderten Felder zurück"""
        if not self.old_values or not self.new_values:
            return {}
        
        changes = {}
        old = self.old_values
        new = self.new_values
        
        for key in new.keys():
            if key in old and old[key] != new[key]:
                changes[key] = {
                    "old": old[key],
                    "new": new[key]
                }
            elif key not in old:
                changes[key] = {
                    "old": None,
                    "new": new[key]
                }
        
        for key in old.keys():
            if key not in new:
                changes[key] = {
                    "old": old[key],
                    "new": None
                }
        
        return changes


# Zirkuläre Importe auflösen
from .user import User
