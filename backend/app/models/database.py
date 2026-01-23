"""
Database model
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.core.database import Base


class DatabaseType(str, enum.Enum):
    """Database type enumeration"""
    MYSQL = "mysql"
    MARIADB = "mariadb"


class Database(Base):
    """Database model"""
    __tablename__ = "databases"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, index=True, nullable=False)  # Database name
    db_type = Column(Enum(DatabaseType), nullable=False)
    
    # Site association
    site_id = Column(Integer, ForeignKey("sites.id", ondelete="CASCADE"), nullable=False)
    
    # Credentials (encrypted)
    username = Column(String(100), nullable=False)  # Database user
    encrypted_password = Column(Text, nullable=False)  # Encrypted password
    
    # Connection info
    host = Column(String(255), default="localhost")
    port = Column(Integer, default=3306)
    
    # Metadata
    description = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    site = relationship("Site", back_populates="databases")
    
    def __repr__(self):
        return f"<Database {self.name}>"
