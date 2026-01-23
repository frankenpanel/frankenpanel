"""
Audit log schemas
"""
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime
from app.models.audit import AuditAction


class AuditLogResponse(BaseModel):
    id: int
    user_id: Optional[int] = None
    username: Optional[str] = None
    action: AuditAction
    resource_type: Optional[str] = None
    resource_id: Optional[int] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    request_path: Optional[str] = None
    request_method: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    success: bool
    error_message: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True
