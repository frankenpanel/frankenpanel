"""
Audit logging utilities
"""
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.audit import AuditLog, AuditAction
from app.core.database import get_db
from typing import Optional, Dict, Any
import json


async def log_audit(
    user_id: Optional[int] = None,
    username: Optional[str] = None,
    action: AuditAction = AuditAction.READ,
    resource_type: Optional[str] = None,
    resource_id: Optional[int] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    request_path: Optional[str] = None,
    request_method: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
    success: bool = True,
    error_message: Optional[str] = None,
    db: Optional[AsyncSession] = None,
) -> AuditLog:
    """Create an audit log entry"""
    if not db:
        async for session in get_db():
            db = session
            break
    
    audit_log = AuditLog(
        user_id=user_id,
        username=username,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        ip_address=ip_address,
        user_agent=user_agent,
        request_path=request_path,
        request_method=request_method,
        details=details or {},
        success=success,
        error_message=error_message,
    )
    
    db.add(audit_log)
    await db.commit()
    await db.refresh(audit_log)
    
    return audit_log
