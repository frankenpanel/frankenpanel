"""
API v1 routes
"""
from fastapi import APIRouter
from app.api.v1 import auth, users, sites, databases, domains, backups, audit

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(sites.router, prefix="/sites", tags=["sites"])
api_router.include_router(databases.router, prefix="/databases", tags=["databases"])
api_router.include_router(domains.router, prefix="/domains", tags=["domains"])
api_router.include_router(backups.router, prefix="/backups", tags=["backups"])
api_router.include_router(audit.router, prefix="/audit", tags=["audit"])
