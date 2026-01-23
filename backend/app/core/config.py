"""
Application configuration and settings
"""
from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    APP_NAME: str = "FrankenPanel Backend"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "production"
    
    # API
    API_V1_PREFIX: str = "/api/v1"
    API_DOCS_URL: Optional[str] = "/docs"
    API_REDOC_URL: Optional[str] = "/redoc"
    
    # Server
    HOST: str = "127.0.0.1"
    PORT: int = 8000
    WORKERS: int = 4
    
    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    SESSION_COOKIE_NAME: str = "frankenpanel_session"
    SESSION_COOKIE_SECURE: bool = True
    SESSION_COOKIE_HTTPONLY: bool = True
    SESSION_COOKIE_SAMESITE: str = "lax"
    
    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "https://localhost"]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: list[str] = ["*"]
    CORS_ALLOW_HEADERS: list[str] = ["*"]
    
    # Database - PostgreSQL (Backend)
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "frankenpanel"
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str = "frankenpanel"
    POSTGRES_POOL_SIZE: int = 20
    POSTGRES_MAX_OVERFLOW: int = 10
    
    # Database - MySQL/MariaDB (Per-site)
    MYSQL_HOST: str = "localhost"
    MYSQL_PORT: int = 3306
    MYSQL_ROOT_USER: str = "root"
    MYSQL_ROOT_PASSWORD: str
    MYSQL_SOCKET: Optional[str] = None
    
    # Paths
    FRANKENPANEL_ROOT: str = "/opt/frankenpanel"
    SITES_DIR: str = "/opt/frankenpanel/sites"
    BACKUPS_DIR: str = "/opt/frankenpanel/backups"
    LOGS_DIR: str = "/opt/frankenpanel/logs"
    CONFIG_DIR: str = "/opt/frankenpanel/config"
    RUNTIME_DIR: str = "/opt/frankenpanel/runtime"
    
    # FrankenPHP
    FRANKENPHP_BIN: str = "/usr/local/bin/frankenphp"
    FRANKENPHP_WORKER_START_PORT: int = 8081
    FRANKENPHP_WORKER_MAX: int = 1000
    
    # Caddy
    CADDY_BIN: str = "/usr/bin/caddy"
    CADDY_CONFIG_DIR: str = "/etc/caddy"
    CADDY_CONFIG_FILE: str = "/etc/caddy/Caddyfile"
    
    # Encryption
    ENCRYPTION_KEY: str  # For encrypting database credentials
    
    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_PER_HOUR: int = 1000
    
    # Backup
    BACKUP_RETENTION_DAYS: int = 30
    BACKUP_ENCRYPTION_ENABLED: bool = True
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    LOG_FILE: str = "/opt/frankenpanel/logs/backend.log"
    
    # Monitoring
    METRICS_ENABLED: bool = True
    METRICS_PORT: int = 9090
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()
