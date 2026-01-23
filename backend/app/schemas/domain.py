"""
Domain schemas
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from app.models.domain import DomainType


class DomainBase(BaseModel):
    domain: str = Field(..., min_length=1, max_length=255)
    domain_type: DomainType = DomainType.PRIMARY
    ssl_enabled: bool = True


class DomainCreate(DomainBase):
    site_id: int


class DomainUpdate(BaseModel):
    ssl_enabled: Optional[bool] = None
    is_active: Optional[bool] = None


class DomainResponse(DomainBase):
    id: int
    site_id: int
    is_active: bool
    ssl_certificate_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
