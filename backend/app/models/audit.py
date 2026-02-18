"""
Audit log model
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Enum, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.core.database import Base


class AuditAction(str, enum.Enum):
    """Audit action types"""
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    LOGIN = "login"
    LOGOUT = "logout"
    PERMISSION_DENIED = "permission_denied"
    CONFIG_CHANGE = "config_change"


class AuditLog(Base):
    """Audit log model"""
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # User info
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    username = Column(String(100))  # Denormalized for historical records
    
    # Action info
    action = Column(Enum(AuditAction), nullable=False)
    resource_type = Column(String(100))  # e.g., "site", "database", "user"
    resource_id = Column(Integer)  # ID of the resource
    
    # Request info
    ip_address = Column(String(45))  # IPv4 or IPv6
    user_agent = Column(Text)
    request_path = Column(String(512))
    request_method = Column(String(10))
    
    # Details
    details = Column(JSON)  # Additional context
    success = Column(Boolean, default=True)
    error_message = Column(Text)
    
    # Timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # Relationships
    user = relationship("User", back_populates="audit_logs")
    
    def __repr__(self):
        return f"<AuditLog {self.action} by {self.username}>"
