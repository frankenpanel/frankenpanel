"""
Database schemas
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from app.models.database import DatabaseType


class DatabaseBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    db_type: DatabaseType = DatabaseType.MYSQL
    description: Optional[str] = None


class DatabaseCreate(DatabaseBase):
    site_id: int
    password: Optional[str] = Field(None, min_length=8)  # Auto-generated if not provided


class DatabaseUpdate(BaseModel):
    description: Optional[str] = None
    password: Optional[str] = Field(None, min_length=8)  # Rotate password


class DatabaseResponse(DatabaseBase):
    id: int
    site_id: int
    username: str
    host: str
    port: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
