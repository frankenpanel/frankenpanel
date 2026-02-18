"""
Site management endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.core.database import get_db
from app.core.middleware import get_current_user
from app.core.audit import log_audit, AuditAction
from app.core.permissions import Resource, Action
from app.core.middleware import require_permission
from app.models.user import User
from app.schemas.site import SiteCreate, SiteUpdate, SiteResponse, SiteStatusUpdate
from app.services.site_service import SiteService

router = APIRouter()


@router.get("/", response_model=List[SiteResponse])
async def list_sites(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all sites"""
    if not await require_permission(Resource.SITE, Action.READ, current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")
    
    service = SiteService(db)
    sites = await service.list_sites()
    return [SiteResponse.model_validate(site) for site in sites[skip:skip+limit]]


@router.post("/", response_model=SiteResponse, status_code=status.HTTP_201_CREATED)
async def create_site(
    site_data: SiteCreate = Body(..., embed=False),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new site"""
    if not await require_permission(Resource.SITE, Action.CREATE, current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")
    
    service = SiteService(db)
    try:
        site = await service.create_site(site_data, current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    await log_audit(
        user_id=current_user.id,
        username=current_user.username,
        action=AuditAction.CREATE,
        resource_type=Resource.SITE,
        resource_id=site.id,
        success=True,
        db=db,
    )
    
    return SiteResponse.model_validate(site)


@router.get("/{site_id}", response_model=SiteResponse)
async def get_site(
    site_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a site by ID"""
    if not await require_permission(Resource.SITE, Action.READ, current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")
    
    service = SiteService(db)
    site = await service.get_site(site_id)
    
    if not site:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Site not found")
    
    return SiteResponse.model_validate(site)


@router.put("/{site_id}", response_model=SiteResponse)
async def update_site(
    site_id: int,
    site_data: SiteUpdate = Body(..., embed=False),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update a site"""
    if not await require_permission(Resource.SITE, Action.UPDATE, current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")
    
    service = SiteService(db)
    site = await service.update_site(site_id, site_data)
    
    await log_audit(
        user_id=current_user.id,
        username=current_user.username,
        action=AuditAction.UPDATE,
        resource_type=Resource.SITE,
        resource_id=site_id,
        success=True,
        db=db,
    )
    
    return SiteResponse.model_validate(site)


@router.delete("/{site_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_site(
    site_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a site"""
    if not await require_permission(Resource.SITE, Action.DELETE, current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")
    
    service = SiteService(db)
    await service.delete_site(site_id)
    
    await log_audit(
        user_id=current_user.id,
        username=current_user.username,
        action=AuditAction.DELETE,
        resource_type=Resource.SITE,
        resource_id=site_id,
        success=True,
        db=db,
    )


@router.post("/{site_id}/start", status_code=status.HTTP_200_OK)
async def start_site(
    site_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Start a site"""
    if not await require_permission(Resource.SITE, Action.UPDATE, current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")
    
    service = SiteService(db)
    await service.start_site(site_id)
    
    return {"message": "Site started successfully"}


@router.post("/{site_id}/stop", status_code=status.HTTP_200_OK)
async def stop_site(
    site_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Stop a site"""
    if not await require_permission(Resource.SITE, Action.UPDATE, current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")
    
    service = SiteService(db)
    await service.stop_site(site_id)
    
    return {"message": "Site stopped successfully"}
