"""
Permission definitions and utilities
"""
from enum import Enum


class Resource(str, Enum):
    """Resource types"""
    USER = "user"
    ROLE = "role"
    SITE = "site"
    DATABASE = "database"
    DOMAIN = "domain"
    BACKUP = "backup"
    SYSTEM = "system"


class Action(str, Enum):
    """Action types"""
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    MANAGE = "manage"  # Full control


# Permission names
PERMISSIONS = {
    # User permissions
    "user:create": {"resource": Resource.USER, "action": Action.CREATE},
    "user:read": {"resource": Resource.USER, "action": Action.READ},
    "user:update": {"resource": Resource.USER, "action": Action.UPDATE},
    "user:delete": {"resource": Resource.USER, "action": Action.DELETE},
    "user:manage": {"resource": Resource.USER, "action": Action.MANAGE},
    
    # Role permissions
    "role:create": {"resource": Resource.ROLE, "action": Action.CREATE},
    "role:read": {"resource": Resource.ROLE, "action": Action.READ},
    "role:update": {"resource": Resource.ROLE, "action": Action.UPDATE},
    "role:delete": {"resource": Resource.ROLE, "action": Action.DELETE},
    
    # Site permissions
    "site:create": {"resource": Resource.SITE, "action": Action.CREATE},
    "site:read": {"resource": Resource.SITE, "action": Action.READ},
    "site:update": {"resource": Resource.SITE, "action": Action.UPDATE},
    "site:delete": {"resource": Resource.SITE, "action": Action.DELETE},
    "site:manage": {"resource": Resource.SITE, "action": Action.MANAGE},
    
    # Database permissions
    "database:create": {"resource": Resource.DATABASE, "action": Action.CREATE},
    "database:read": {"resource": Resource.DATABASE, "action": Action.READ},
    "database:update": {"resource": Resource.DATABASE, "action": Action.UPDATE},
    "database:delete": {"resource": Resource.DATABASE, "action": Action.DELETE},
    
    # Domain permissions
    "domain:create": {"resource": Resource.DOMAIN, "action": Action.CREATE},
    "domain:read": {"resource": Resource.DOMAIN, "action": Action.READ},
    "domain:update": {"resource": Resource.DOMAIN, "action": Action.UPDATE},
    "domain:delete": {"resource": Resource.DOMAIN, "action": Action.DELETE},
    
    # Backup permissions
    "backup:create": {"resource": Resource.BACKUP, "action": Action.CREATE},
    "backup:read": {"resource": Resource.BACKUP, "action": Action.READ},
    "backup:restore": {"resource": Resource.BACKUP, "action": Action.UPDATE},
    "backup:delete": {"resource": Resource.BACKUP, "action": Action.DELETE},
    
    # System permissions
    "system:manage": {"resource": Resource.SYSTEM, "action": Action.MANAGE},
}


def get_permission_name(resource: Resource, action: Action) -> str:
    """Get permission name from resource and action"""
    return f"{resource.value}:{action.value}"
