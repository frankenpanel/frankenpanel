"""
SSL Certificate model
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class SSLCertificate(Base):
    """SSL Certificate model"""
    __tablename__ = "ssl_certificates"
    
    id = Column(Integer, primary_key=True, index=True)
    domain = Column(String(255), unique=True, index=True, nullable=False)
    
    # Certificate info
    issuer = Column(String(255))
    issued_at = Column(DateTime(timezone=True))
    expires_at = Column(DateTime(timezone=True))
    auto_renew = Column(Boolean, default=True)
    
    # Caddy-managed certificates
    caddy_managed = Column(Boolean, default=True)
    caddy_config = Column(JSON, default=dict)
    
    # Status
    is_valid = Column(Boolean, default=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    domains = relationship("Domain", back_populates="ssl_certificate")
    
    def __repr__(self):
        return f"<SSLCertificate {self.domain}>"
