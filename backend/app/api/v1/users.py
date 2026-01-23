"""
User management endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from app.core.database import get_db
from app.core.middleware import get_current_user, require_permission
from app.core.audit import log_audit, AuditAction
from app.models.user import User, Role, Permission
from app.schemas.user import UserCreate, UserUpdate, UserResponse, RoleCreate, RoleUpdate, RoleResponse
from app.services.user_service import UserService
from app.core.permissions import Resource, Action

router = APIRouter()


@router.get("/", response_model=List[UserResponse])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all users"""
    if not await require_permission(Resource.USER, Action.READ, current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")
    
    result = await db.execute(select(User).offset(skip).limit(limit))
    users = result.scalars().all()
    return [UserResponse.model_validate(user) for user in users]


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new user"""
    if not await require_permission(Resource.USER, Action.CREATE, current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")
    
    service = UserService(db)
    user = await service.create_user(user_data)
    
    await log_audit(
        user_id=current_user.id,
        username=current_user.username,
        action=AuditAction.CREATE,
        resource_type=Resource.USER,
        resource_id=user.id,
        success=True,
        db=db,
    )
    
    return UserResponse.model_validate(user)


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a user by ID"""
    if not await require_permission(Resource.USER, Action.READ, current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")
    
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    return UserResponse.model_validate(user)


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update a user"""
    if not await require_permission(Resource.USER, Action.UPDATE, current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")
    
    service = UserService(db)
    user = await service.update_user(user_id, user_data)
    
    await log_audit(
        user_id=current_user.id,
        username=current_user.username,
        action=AuditAction.UPDATE,
        resource_type=Resource.USER,
        resource_id=user_id,
        success=True,
        db=db,
    )
    
    return UserResponse.model_validate(user)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a user"""
    if not await require_permission(Resource.USER, Action.DELETE, current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")
    
    service = UserService(db)
    await service.delete_user(user_id)
    
    await log_audit(
        user_id=current_user.id,
        username=current_user.username,
        action=AuditAction.DELETE,
        resource_type=Resource.USER,
        resource_id=user_id,
        success=True,
        db=db,
    )


@router.get("/roles/", response_model=List[RoleResponse])
async def list_roles(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all roles"""
    result = await db.execute(select(Role))
    roles = result.scalars().all()
    return [RoleResponse.model_validate(role) for role in roles]


@router.post("/roles/", response_model=RoleResponse, status_code=status.HTTP_201_CREATED)
async def create_role(
    role_data: RoleCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new role"""
    if not await require_permission(Resource.ROLE, Action.CREATE, current_user):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied")
    
    service = UserService(db)
    role = await service.create_role(role_data)
    
    return RoleResponse.model_validate(role)
