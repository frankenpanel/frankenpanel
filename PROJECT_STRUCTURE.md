# FrankenPanel Project Structure

## Complete Directory Tree

```
FrankenPanel/
├── backend/                          # FastAPI Backend
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                   # FastAPI application entry point
│   │   ├── api/                      # API routes
│   │   │   ├── __init__.py
│   │   │   └── v1/
│   │   │       ├── __init__.py
│   │   │       ├── auth.py           # Authentication endpoints
│   │   │       ├── users.py          # User management
│   │   │       ├── sites.py          # Site management
│   │   │       ├── databases.py      # Database management
│   │   │       ├── domains.py        # Domain management
│   │   │       ├── backups.py        # Backup management
│   │   │       └── audit.py          # Audit logs
│   │   ├── core/                     # Core utilities
│   │   │   ├── __init__.py
│   │   │   ├── config.py             # Configuration settings
│   │   │   ├── database.py           # Database connection
│   │   │   ├── security.py           # Security utilities
│   │   │   ├── middleware.py        # Middleware
│   │   │   ├── audit.py              # Audit logging
│   │   │   └── permissions.py        # Permission definitions
│   │   ├── models/                   # SQLAlchemy models
│   │   │   ├── __init__.py
│   │   │   ├── user.py               # User, Role, Permission
│   │   │   ├── site.py               # Site model
│   │   │   ├── database.py           # Database model
│   │   │   ├── domain.py             # Domain model
│   │   │   ├── ssl.py                # SSL certificate model
│   │   │   ├── backup.py             # Backup model
│   │   │   └── audit.py              # Audit log model
│   │   ├── schemas/                  # Pydantic schemas
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── site.py
│   │   │   ├── database.py
│   │   │   ├── domain.py
│   │   │   ├── backup.py
│   │   │   └── audit.py
│   │   └── services/                 # Business logic
│   │       ├── __init__.py
│   │       ├── user_service.py
│   │       ├── site_service.py
│   │       ├── database_service.py
│   │       ├── domain_service.py
│   │       ├── backup_service.py
│   │       ├── frankenphp_service.py
│   │       └── caddy_service.py
│   ├── alembic/                      # Database migrations
│   │   ├── env.py
│   │   ├── script.py.mako
│   │   └── versions/
│   ├── alembic.ini
│   ├── requirements.txt
│   ├── pyproject.toml
│   └── .env                          # Environment variables (not in repo)
│
├── frontend/                         # React Frontend
│   ├── src/
│   │   ├── App.tsx                   # Main app component
│   │   ├── main.tsx                  # Entry point
│   │   ├── index.css                 # Global styles
│   │   ├── components/               # React components
│   │   │   ├── Layout.tsx
│   │   │   └── ProtectedRoute.tsx
│   │   ├── pages/                    # Page components
│   │   │   ├── Login.tsx
│   │   │   ├── Dashboard.tsx
│   │   │   ├── Sites.tsx
│   │   │   ├── SiteDetail.tsx
│   │   │   ├── Databases.tsx
│   │   │   ├── Domains.tsx
│   │   │   ├── Backups.tsx
│   │   │   ├── Users.tsx
│   │   │   └── AuditLogs.tsx
│   │   ├── contexts/                 # React contexts
│   │   │   └── AuthContext.tsx
│   │   ├── hooks/                    # Custom hooks
│   │   └── services/                 # API services
│   │       └── api.ts
│   ├── package.json
│   ├── vite.config.ts
│   ├── tsconfig.json
│   ├── tailwind.config.js
│   └── index.html
│
├── scripts/                          # Utility scripts
│   └── install.sh                    # Installation script
│
├── docs/                             # Documentation
│   ├── ARCHITECTURE.md               # System architecture
│   ├── API.md                        # API documentation
│   ├── SECURITY.md                   # Security guide
│   ├── DEPLOYMENT.md                 # Deployment guide
│   ├── DEVELOPER.md                  # Developer guide
│   ├── ARCHITECTURE_DIAGRAM.txt      # ASCII architecture diagram
│   └── SITE_ORCHESTRATION.md         # Site lifecycle documentation
│
├── README.md                          # Main README
├── LICENSE                            # MIT License
├── CONTRIBUTING.md                    # Contribution guidelines
├── PROJECT_STRUCTURE.md              # This file
└── .gitignore                         # Git ignore rules

## Runtime Structure (after installation)

```
/opt/frankenpanel/
├── control-panel/                    # Backend + Frontend
│   ├── backend/                      # FastAPI application
│   │   ├── venv/                     # Python virtual environment
│   │   ├── app/                      # Application code
│   │   └── .env                      # Configuration
│   └── frontend/                     # React build output
│       └── dist/                     # Built frontend files
│
├── sites/                            # PHP site directories
│   ├── site1/                        # WordPress site
│   │   ├── wp-config.php
│   │   └── ... (WordPress files)
│   ├── site2/                        # Joomla site
│   │   └── ... (Joomla files)
│   └── site3/                        # Custom PHP site
│       └── ... (Custom files)
│
├── databases/                        # MySQL metadata (not actual DBs)
│
├── backups/                          # Encrypted backups
│   ├── backup_site1_20240101_120000.tar.gz
│   └── ...
│
├── logs/                             # System and site logs
│   ├── backend.log
│   ├── frankenphp_1.log
│   └── ...
│
├── config/                           # Generated configurations
│
└── runtime/                          # FrankenPHP workers
    ├── worker_1.json
    ├── worker_1.pid
    └── ...
```

## Key Files

### Backend
- `app/main.py` - FastAPI application
- `app/core/config.py` - Configuration management
- `app/core/database.py` - Database connection
- `app/core/security.py` - Security utilities
- `app/services/*.py` - Business logic services
- `app/api/v1/*.py` - API endpoints

### Frontend
- `src/App.tsx` - Main React application
- `src/pages/*.tsx` - Page components
- `src/components/*.tsx` - Reusable components
- `src/contexts/AuthContext.tsx` - Authentication context

### Configuration
- `backend/.env` - Environment variables
- `/etc/caddy/Caddyfile` - Caddy configuration
- `/etc/systemd/system/frankenpanel-backend.service` - Systemd service

## Database Schema

### PostgreSQL (Backend Metadata)
- `users` - User accounts
- `roles` - User roles
- `permissions` - Permission definitions
- `user_role` - User-role mapping
- `role_permission` - Role-permission mapping
- `sites` - Site metadata
- `databases` - Database metadata (encrypted passwords)
- `domains` - Domain mappings
- `ssl_certificates` - SSL certificate records
- `backups` - Backup records
- `audit_logs` - Audit trail

### MySQL/MariaDB (Per-Site Databases)
- Each site has its own database
- Database names: `{site_slug}_db`
- Isolated from other sites

## Port Allocation

- `8000` - FastAPI backend (127.0.0.1)
- `8081+` - FrankenPHP workers (one per site, 127.0.0.1)
- `80/443` - Caddy (public)

## Service Management

- `frankenpanel-backend` - FastAPI backend service
- `caddy` - Reverse proxy service
- `postgresql` - PostgreSQL database
- `mysql` - MySQL/MariaDB database
