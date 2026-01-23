"""
Backup schemas
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from app.models.backup import BackupType, BackupStatus


class BackupCreate(BaseModel):
    site_id: int
    backup_type: BackupType = BackupType.FULL
    description: Optional[str] = None


class BackupResponse(BaseModel):
    id: int
    site_id: int
    backup_type: BackupType
    status: BackupStatus
    file_path: str
    file_size: Optional[int] = None
    encrypted: bool
    description: Optional[str] = None
    created_by: Optional[int] = None
    created_at: datetime
    completed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class BackupRestoreRequest(BaseModel):
    backup_id: int
    site_id: int
    restore_database: bool = True
    restore_files: bool = True
