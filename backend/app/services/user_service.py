"""
User management service
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User, Role, Permission
from app.schemas.user import UserCreate, UserUpdate, RoleCreate, RoleUpdate
from app.core.security import get_password_hash
from typing import Optional


class UserService:
    """Service for managing users"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_user(self, user_data: UserCreate) -> User:
        """Create a new user"""
        # Check if user exists
        result = await self.db.execute(select(User).where(User.username == user_data.username))
        if result.scalar_one_or_none():
            raise ValueError(f"Username {user_data.username} already exists")
        
        result = await self.db.execute(select(User).where(User.email == user_data.email))
        if result.scalar_one_or_none():
            raise ValueError(f"Email {user_data.email} already exists")
        
        # Create user
        user = User(
            username=user_data.username,
            email=user_data.email,
            full_name=user_data.full_name,
            hashed_password=get_password_hash(user_data.password),
        )
        
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        
        return user
    
    async def update_user(self, user_id: int, user_data: UserUpdate) -> User:
        """Update a user"""
        result = await self.db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        
        if not user:
            raise ValueError(f"User {user_id} not found")
        
        if user_data.username:
            # Check if username is taken
            result = await self.db.execute(
                select(User).where(User.username == user_data.username, User.id != user_id)
            )
            if result.scalar_one_or_none():
                raise ValueError(f"Username {user_data.username} already exists")
            user.username = user_data.username
        
        if user_data.email:
            # Check if email is taken
            result = await self.db.execute(
                select(User).where(User.email == user_data.email, User.id != user_id)
            )
            if result.scalar_one_or_none():
                raise ValueError(f"Email {user_data.email} already exists")
            user.email = user_data.email
        
        if user_data.full_name is not None:
            user.full_name = user_data.full_name
        
        if user_data.is_active is not None:
            user.is_active = user_data.is_active
        
        if user_data.password:
            user.hashed_password = get_password_hash(user_data.password)
        
        await self.db.commit()
        await self.db.refresh(user)
        
        return user
    
    async def delete_user(self, user_id: int) -> bool:
        """Delete a user"""
        result = await self.db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        
        if not user:
            raise ValueError(f"User {user_id} not found")
        
        await self.db.delete(user)
        await self.db.commit()
        
        return True
    
    async def create_role(self, role_data: RoleCreate) -> Role:
        """Create a new role"""
        # Check if role exists
        result = await self.db.execute(select(Role).where(Role.name == role_data.name))
        if result.scalar_one_or_none():
            raise ValueError(f"Role {role_data.name} already exists")
        
        # Create role
        role = Role(
            name=role_data.name,
            description=role_data.description,
        )
        
        self.db.add(role)
        await self.db.flush()
        
        # Add permissions
        if role_data.permission_ids:
            result = await self.db.execute(
                select(Permission).where(Permission.id.in_(role_data.permission_ids))
            )
            permissions = result.scalars().all()
            role.permissions = list(permissions)
        
        await self.db.commit()
        await self.db.refresh(role)
        
        return role
