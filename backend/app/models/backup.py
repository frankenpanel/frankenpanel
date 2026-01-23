"""
Backup model
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.core.database import Base


class BackupType(str, enum.Enum):
    """Backup type enumeration"""
    FULL = "full"  # Site + database
    SITE_ONLY = "site_only"
    DATABASE_ONLY = "database_only"


class BackupStatus(str, enum.Enum):
    """Backup status enumeration"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class Backup(Base):
    """Backup model"""
    __tablename__ = "backups"
    
    id = Column(Integer, primary_key=True, index=True)
    site_id = Column(Integer, ForeignKey("sites.id", ondelete="CASCADE"), nullable=False)
    
    # Backup info
    backup_type = Column(Enum(BackupType), nullable=False)
    status = Column(Enum(BackupStatus), default=BackupStatus.PENDING)
    
    # File info
    file_path = Column(String(512), nullable=False)
    file_size = Column(Integer)  # Size in bytes
    encrypted = Column(Boolean, default=True)
    
    # Metadata
    description = Column(Text)
    created_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    site = relationship("Site", back_populates="backups")
    
    def __repr__(self):
        return f"<Backup {self.id} for site {self.site_id}>"
