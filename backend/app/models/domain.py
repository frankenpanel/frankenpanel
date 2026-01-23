"""
Domain model
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.core.database import Base


class DomainType(str, enum.Enum):
    """Domain type enumeration"""
    PRIMARY = "primary"
    ALIAS = "alias"
    SUBDOMAIN = "subdomain"


class Domain(Base):
    """Domain model"""
    __tablename__ = "domains"
    
    id = Column(Integer, primary_key=True, index=True)
    domain = Column(String(255), unique=True, index=True, nullable=False)  # example.com, www.example.com
    domain_type = Column(Enum(DomainType), nullable=False)
    
    # Site association
    site_id = Column(Integer, ForeignKey("sites.id", ondelete="CASCADE"), nullable=False)
    
    # SSL
    ssl_enabled = Column(Boolean, default=True)
    ssl_certificate_id = Column(Integer, ForeignKey("ssl_certificates.id", ondelete="SET NULL"), nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    site = relationship("Site", back_populates="domains")
    ssl_certificate = relationship("SSLCertificate", back_populates="domains")
    
    def __repr__(self):
        return f"<Domain {self.domain}>"
