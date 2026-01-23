"""
Site schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from app.models.site import SiteType, SiteStatus


class SiteBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    site_type: SiteType
    description: Optional[str] = None
    php_version: str = Field(default="8.2", pattern=r"^\d+\.\d+$")
    config: Optional[Dict[str, Any]] = None


class SiteCreate(SiteBase):
    domain: str = Field(..., description="Primary domain for the site")
    create_database: bool = Field(default=True, description="Create database automatically")


class SiteUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    php_version: Optional[str] = Field(None, pattern=r"^\d+\.\d+$")
    config: Optional[Dict[str, Any]] = None


class SiteStatusUpdate(BaseModel):
    status: SiteStatus


class SiteResponse(SiteBase):
    id: int
    slug: str
    status: SiteStatus
    path: str
    worker_port: int
    owner_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
