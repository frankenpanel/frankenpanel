"""
Domain management endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.core.database import get_db
from app.core.middleware import get_current_user
from app.core.audit import log_audit, AuditAction
from app.core.permissions import Resource, Action
from app.core.middleware import require_permission
from app.models.user import User
from app.schemas.domain import DomainCreate, DomainUpdate, DomainResponse
from app.services.domain_service import DomainService

router = APIRouter()


@router.get("/", response_model=List[DomainResponse])
async def list_domains(
    site_id: int = None,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List domains"""
    if not await require_permission(Resource.DOMAIN, Action.READ, current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")
    
    service = DomainService(db)
    domains = await service.list_domains(site_id=site_id)
    return [DomainResponse.model_validate(d) for d in domains[skip:skip+limit]]


@router.post("/", response_model=DomainResponse, status_code=status.HTTP_201_CREATED)
async def create_domain(
    domain_data: DomainCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new domain"""
    if not await require_permission(Resource.DOMAIN, Action.CREATE, current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")
    
    service = DomainService(db)
    domain = await service.create_domain(
        domain=domain_data.domain,
        site_id=domain_data.site_id,
        domain_type=domain_data.domain_type,
        ssl_enabled=domain_data.ssl_enabled,
    )
    
    await log_audit(
        user_id=current_user.id,
        username=current_user.username,
        action=AuditAction.CREATE,
        resource_type=Resource.DOMAIN,
        resource_id=domain.id,
        success=True,
        db=db,
    )
    
    return DomainResponse.model_validate(domain)


@router.put("/{domain_id}", response_model=DomainResponse)
async def update_domain(
    domain_id: int,
    domain_data: DomainUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update a domain"""
    if not await require_permission(Resource.DOMAIN, Action.UPDATE, current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")
    
    service = DomainService(db)
    domain = await service.update_domain(domain_id, domain_data)
    
    await log_audit(
        user_id=current_user.id,
        username=current_user.username,
        action=AuditAction.UPDATE,
        resource_type=Resource.DOMAIN,
        resource_id=domain_id,
        success=True,
        db=db,
    )
    
    return DomainResponse.model_validate(domain)


@router.delete("/{domain_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_domain(
    domain_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a domain"""
    if not await require_permission(Resource.DOMAIN, Action.DELETE, current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")
    
    service = DomainService(db)
    await service.delete_domain(domain_id)
    
    await log_audit(
        user_id=current_user.id,
        username=current_user.username,
        action=AuditAction.DELETE,
        resource_type=Resource.DOMAIN,
        resource_id=domain_id,
        success=True,
        db=db,
    )
