"""
Database management endpoints
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
from app.schemas.database import DatabaseCreate, DatabaseUpdate, DatabaseResponse
from app.services.database_service import DatabaseService

router = APIRouter()


@router.get("/", response_model=List[DatabaseResponse])
async def list_databases(
    site_id: int = None,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List databases"""
    if not await require_permission(Resource.DATABASE, Action.READ, current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")
    
    service = DatabaseService(db)
    databases = await service.list_databases(site_id=site_id)
    return [DatabaseResponse.model_validate(db) for db in databases[skip:skip+limit]]


@router.post("/", response_model=DatabaseResponse, status_code=status.HTTP_201_CREATED)
async def create_database(
    db_data: DatabaseCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new database"""
    if not await require_permission(Resource.DATABASE, Action.CREATE, current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")
    
    service = DatabaseService(db)
    database = await service.create_database(
        site_id=db_data.site_id,
        name=db_data.name,
        db_type=db_data.db_type,
        password=db_data.password,
    )
    
    await log_audit(
        user_id=current_user.id,
        username=current_user.username,
        action=AuditAction.CREATE,
        resource_type=Resource.DATABASE,
        resource_id=database.id,
        success=True,
        db=db,
    )
    
    return DatabaseResponse.model_validate(database)


@router.get("/{database_id}", response_model=DatabaseResponse)
async def get_database(
    database_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a database by ID"""
    if not await require_permission(Resource.DATABASE, Action.READ, current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")
    
    service = DatabaseService(db)
    database = await service.get_database(database_id)
    
    if not database:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Database not found")
    
    return DatabaseResponse.model_validate(database)


@router.put("/{database_id}", response_model=DatabaseResponse)
async def update_database(
    database_id: int,
    db_data: DatabaseUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update a database"""
    if not await require_permission(Resource.DATABASE, Action.UPDATE, current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")
    
    service = DatabaseService(db)
    
    if db_data.password:
        database = await service.update_database_password(database_id, db_data.password)
    else:
        database = await service.get_database(database_id)
        if db_data.description:
            database.description = db_data.description
            await db.commit()
            await db.refresh(database)
    
    await log_audit(
        user_id=current_user.id,
        username=current_user.username,
        action=AuditAction.UPDATE,
        resource_type=Resource.DATABASE,
        resource_id=database_id,
        success=True,
        db=db,
    )
    
    return DatabaseResponse.model_validate(database)


@router.delete("/{database_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_database(
    database_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a database"""
    if not await require_permission(Resource.DATABASE, Action.DELETE, current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")
    
    service = DatabaseService(db)
    await service.delete_database(database_id)
    
    await log_audit(
        user_id=current_user.id,
        username=current_user.username,
        action=AuditAction.DELETE,
        resource_type=Resource.DATABASE,
        resource_id=database_id,
        success=True,
        db=db,
    )
