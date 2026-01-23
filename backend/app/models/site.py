"""
Site model
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Enum, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.core.database import Base


class SiteType(str, enum.Enum):
    """Site type enumeration"""
    WORDPRESS = "wordpress"
    JOOMLA = "joomla"
    CUSTOM_PHP = "custom_php"
    STATIC = "static"


class SiteStatus(str, enum.Enum):
    """Site status enumeration"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    MAINTENANCE = "maintenance"


class Site(Base):
    """Site model"""
    __tablename__ = "sites"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, index=True, nullable=False)
    slug = Column(String(255), unique=True, index=True, nullable=False)  # URL-safe identifier
    site_type = Column(Enum(SiteType), nullable=False)
    status = Column(Enum(SiteStatus), default=SiteStatus.INACTIVE)
    
    # Paths
    path = Column(String(512), unique=True, nullable=False)  # /opt/frankenpanel/sites/site1
    worker_port = Column(Integer, unique=True, nullable=False)  # 8081, 8082, etc.
    
    # Configuration
    php_version = Column(String(10), default="8.2")
    config = Column(JSON, default=dict)  # Site-specific configuration
    
    # Ownership
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    
    # Metadata
    description = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    owner = relationship("User", back_populates="sites")
    databases = relationship("Database", back_populates="site", cascade="all, delete-orphan")
    domains = relationship("Domain", back_populates="site", cascade="all, delete-orphan")
    backups = relationship("Backup", back_populates="site", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Site {self.name}>"
