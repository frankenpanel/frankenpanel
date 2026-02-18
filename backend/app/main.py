"""
FastAPI main application
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse
from app.core.config import settings
from app.core.database import init_db, close_db
from app.core.middleware import AuditMiddleware, SecurityHeadersMiddleware, PreferFrontendMiddleware
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

# Prefer frontend: redirect browser navigation to /api/* to dashboard (API is only used by the frontend)
app.add_middleware(PreferFrontendMiddleware)

# Include API router
app.include_router(api_router, prefix=settings.API_V1_PREFIX)


@app.get("/health")
async def health_check():
    """Health check (registered before catch-all so /health is not shadowed)."""
    return {
        "status": "healthy",
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
    }


# Serve frontend or fallback so "/" never returns 404
# Vite default build outputs dist/index.html + dist/assets/ (not dist/static/); only mount /static if it exists
frontend_dir = os.path.join(settings.FRANKENPANEL_ROOT, "control-panel", "frontend", "dist")
if os.path.exists(frontend_dir):
    static_subdir = os.path.join(frontend_dir, "static")
    if os.path.isdir(static_subdir):
        app.mount("/static", StaticFiles(directory=static_subdir), name="static")

_FALLBACK_HTML = """<!DOCTYPE html>
<html><head><title>FrankenPanel</title></head>
<body style="font-family:sans-serif;max-width:600px;margin:2em auto;padding:1em;">
  <h1>FrankenPanel</h1>
  <p>Dashboard UI is not built yet. Build the frontend on the server:</p>

  <p>Then restart: <code>sudo systemctl restart frankenpanel-backend</code></p>
  <p><a href="/health">/health</a></p>
</body></html>"""


@app.get("/{full_path:path}")
async def serve_frontend(full_path: str):
    """Serve React frontend or fallback so root and SPA paths always respond."""
    if full_path.startswith("api"):
        return None
    path = full_path or ""
    file_path = os.path.join(frontend_dir, path)
    if os.path.exists(frontend_dir) and os.path.exists(file_path) and os.path.isfile(file_path):
        return FileResponse(file_path)
    index_path = os.path.join(frontend_dir, "index.html")
    if os.path.exists(frontend_dir) and os.path.exists(index_path):
        return FileResponse(index_path)
    return HTMLResponse(status_code=200, content=_FALLBACK_HTML)


@app.on_event("startup")
async def startup_event():
    """Initialize on startup"""
    await init_db()


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    await close_db()
