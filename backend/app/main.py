"""
FastAPI main application
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.core.config import settings
from app.core.database import init_db, close_db
from app.core.middleware import AuditMiddleware, SecurityHeadersMiddleware
from app.api.v1 import api_router
import os

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    docs_url=settings.API_DOCS_URL if settings.DEBUG else None,
    redoc_url=settings.API_REDOC_URL if settings.DEBUG else None,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.CORS_ALLOW_METHODS,
    allow_headers=settings.CORS_ALLOW_HEADERS,
)

# Security headers middleware
app.add_middleware(SecurityHeadersMiddleware)

# Audit logging middleware
if not settings.DEBUG:
    app.add_middleware(AuditMiddleware)

# Include API router
app.include_router(api_router, prefix=settings.API_V1_PREFIX)

# Serve frontend static files
frontend_dir = os.path.join(settings.FRANKENPANEL_ROOT, "control-panel", "frontend", "dist")
if os.path.exists(frontend_dir):
    app.mount("/static", StaticFiles(directory=os.path.join(frontend_dir, "static")), name="static")
    
    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        """Serve React frontend"""
        if full_path.startswith("api"):
            return None  # Let API routes handle it
        
        file_path = os.path.join(frontend_dir, full_path)
        if os.path.exists(file_path) and os.path.isfile(file_path):
            return FileResponse(file_path)
        
        # Serve index.html for SPA routing
        index_path = os.path.join(frontend_dir, "index.html")
        if os.path.exists(index_path):
            return FileResponse(index_path)
        
        return {"error": "Not found"}


@app.on_event("startup")
async def startup_event():
    """Initialize on startup"""
    await init_db()


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    await close_db()


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
    }
