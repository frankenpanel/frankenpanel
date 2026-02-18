"""
Backup management endpoints
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
from app.schemas.backup import BackupCreate, BackupResponse, BackupRestoreRequest
from app.services.backup_service import BackupService

router = APIRouter()


@router.get("/", response_model=List[BackupResponse])
async def list_backups(
    site_id: int = None,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List backups"""
    if not await require_permission(Resource.BACKUP, Action.READ, current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")
    
    from sqlalchemy import select
    from app.models.backup import Backup
    
    query = select(Backup)
    if site_id:
        query = query.where(Backup.site_id == site_id)
    query = query.offset(skip).limit(limit)
    
    result = await db.execute(query)
    backups = result.scalars().all()
    return [BackupResponse.model_validate(b) for b in backups]


@router.post("/", response_model=BackupResponse, status_code=status.HTTP_201_CREATED)
async def create_backup(
    backup_data: BackupCreate = Body(..., embed=False),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a backup"""
    if not await require_permission(Resource.BACKUP, Action.CREATE, current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")
    
    service = BackupService(db)
    backup = await service.create_backup(backup_data, current_user.id)
    
    await log_audit(
        user_id=current_user.id,
        username=current_user.username,
        action=AuditAction.CREATE,
        resource_type=Resource.BACKUP,
        resource_id=backup.id,
        success=True,
        db=db,
    )
    
    return BackupResponse.model_validate(backup)


@router.post("/restore", status_code=status.HTTP_200_OK)
async def restore_backup(
    restore_data: BackupRestoreRequest = Body(..., embed=False),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Restore a backup"""
    if not await require_permission(Resource.BACKUP, Action.UPDATE, current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")
    
    service = BackupService(db)
    await service.restore_backup(restore_data)
    
    await log_audit(
        user_id=current_user.id,
        username=current_user.username,
        action=AuditAction.UPDATE,
        resource_type=Resource.BACKUP,
        resource_id=restore_data.backup_id,
        success=True,
        db=db,
    )
    
    return {"message": "Backup restored successfully"}


@router.get("/{backup_id}", response_model=BackupResponse)
async def get_backup(
    backup_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a backup by ID"""
    if not await require_permission(Resource.BACKUP, Action.READ, current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")
    
    from sqlalchemy import select
    from app.models.backup import Backup
    
    result = await db.execute(select(Backup).where(Backup.id == backup_id))
    backup = result.scalar_one_or_none()
    
    if not backup:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Backup not found")
    
    return BackupResponse.model_validate(backup)


@router.delete("/{backup_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_backup(
    backup_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a backup"""
    if not await require_permission(Resource.BACKUP, Action.DELETE, current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")
    
    from sqlalchemy import select
    from app.models.backup import Backup
    import os
    
    result = await db.execute(select(Backup).where(Backup.id == backup_id))
    backup = result.scalar_one_or_none()
    
    if not backup:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Backup not found")
    
    # Delete file
    if os.path.exists(backup.file_path):
        os.remove(backup.file_path)
    
    await db.delete(backup)
    await db.commit()
    
    await log_audit(
        user_id=current_user.id,
        username=current_user.username,
        action=AuditAction.DELETE,
        resource_type=Resource.BACKUP,
        resource_id=backup_id,
        success=True,
        db=db,
    )
