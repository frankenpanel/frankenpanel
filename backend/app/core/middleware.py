"""
Middleware: authentication, logging, security
"""
from fastapi import Request, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.core.database import get_db
from app.core.security import decode_token
from app.models.user import User, Role
from app.models.audit import AuditAction
from app.core.audit import log_audit
from typing import Callable
import time
import json

security = HTTPBearer(auto_error=False)


async def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials = None,
    db: AsyncSession = Depends(get_db),
) -> User:
    """Get current authenticated user"""
    # When called from middleware (not via Depends), db may not be injected; get session then
    if not isinstance(db, AsyncSession):
        async for session in get_db():
            db = session
            break
    # Try to get token from Authorization header
    token = None
    if credentials:
        token = credentials.credentials
    else:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
    
    # Try to get token from session cookie
    if not token:
        token = request.cookies.get("frankenpanel_session")
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    payload = decode_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    username: str = payload.get("sub")
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )
    
    # Get user from database; eager-load roles and permissions to avoid async lazy-load errors
    from sqlalchemy import select
    result = await db.execute(
        select(User)
        .where(User.username == username)
        .options(selectinload(User.roles).selectinload(Role.permissions))
    )
    user = result.scalar_one_or_none()
    
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )
    
    return user


def _perm_str(v):
    """Normalize resource/action to string for DB comparison (accepts enum or str)."""
    return v.value if hasattr(v, "value") else v


async def require_permission(
    resource: str,
    action: str,
    user: User = None,
    request: Request = None,
    db: AsyncSession = None
) -> bool:
    """Check if user has required permission. resource/action can be Resource/Action enums or strings."""
    if not user:
        if request:
            user = await get_current_user(request)
        else:
            return False
    
    # Superusers have all permissions
    if user.is_superuser:
        return True
    
    # Check user roles and permissions
    if not db:
        async for session in get_db():
            db = session
            break
    
    res_str = _perm_str(resource)
    act_str = _perm_str(action)
    # Get all permissions for user's roles
    for role in user.roles:
        for permission in role.permissions:
            if permission.resource == res_str and permission.action == act_str:
                return True
    
    return False


class AuditMiddleware:
    """Middleware to log all requests"""
    
    async def __call__(self, request: Request, call_next: Callable):
        start_time = time.time()
        
        # Process request
        response = await call_next(request)
        
        # Log request
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        
        # Log to audit if authenticated
        try:
            user = await get_current_user(request)
            await log_audit(
                user_id=user.id,
                action=AuditAction.READ,
                resource_type="api",
                request_path=request.url.path,
                request_method=request.method,
                ip_address=request.client.host if request.client else None,
                user_agent=request.headers.get("user-agent"),
                success=response.status_code < 400,
            )
        except:
            pass  # Not authenticated, skip audit
        
        return response


class SecurityHeadersMiddleware:
    """Add security headers to responses"""
    
    async def __call__(self, request: Request, call_next: Callable):
        response = await call_next(request)
        
        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        
        return response
