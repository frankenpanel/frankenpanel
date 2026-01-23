# FrankenPanel

A production-ready, open-source platform for managing multiple PHP sites (WordPress, Joomla, custom PHP) with FrankenPHP, MySQL/MariaDB, and Caddy reverse proxy.

**Repository**: [https://github.com/frankenpanel/frankenpanel](https://github.com/frankenpanel/frankenpanel)

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         CLIENT BROWSER                           │
│                    (HTTPS via Caddy)                             │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                         CADDY REVERSE PROXY                      │
│  - SSL/TLS termination                                          │
│  - Domain routing                                               │
│  - Load balancing (future)                                      │
└────────────┬───────────────────────────────┬────────────────────┘
             │                               │
             │                               │
    ┌────────▼────────┐            ┌────────▼────────┐
    │  ADMIN DASHBOARD│            │  PHP SITES      │
    │  (React SPA)    │            │  (FrankenPHP)   │
    │  Port: 8000     │            │  Ports: 8081+   │
    └────────┬────────┘            └────────┬────────┘
             │                               │
             │                               │
    ┌────────▼───────────────────────────────▼────────┐
    │         FASTAPI BACKEND (Orchestration)         │
    │  - User management                              │
    │  - Site lifecycle                               │
    │  - Database management                          │
    │  - Domain/SSL management                        │
    │  - Backup/restore                               │
    │  - Audit logging                                │
    └────────┬────────────────────────────────────────┘
             │
    ┌────────▼────────┐
    │   POSTGRESQL    │
    │  (Metadata only)│
    └─────────────────┘
             │
    ┌────────▼────────┐
    │  MYSQL/MARIADB  │
    │  (Per-site DBs) │
    └─────────────────┘
```

## Features

- **Multi-Tenant Architecture**: Isolated sites with dedicated databases
- **FrankenPHP Integration**: Native PHP execution with worker isolation
- **Automatic SSL**: Caddy handles SSL/TLS certificates automatically
- **Role-Based Access Control**: Fine-grained permissions system
- **Audit Logging**: Complete operation history
- **Backup & Restore**: Automated site and database backups
- **REST API**: Full programmatic access
- **Modern Stack**: FastAPI, React, PostgreSQL, MySQL/MariaDB

## Quick Start

### Prerequisites

- Ubuntu 22.04+ / Debian 12+ / macOS (development)
- Python 3.12+
- Root/sudo access for installation

### Installation

```bash
# Clone the repository
git clone https://github.com/frankenpanel/frankenpanel.git
cd frankenpanel

# Run the installer
sudo bash scripts/install.sh

# Start the system
sudo systemctl start frankenpanel-backend
sudo systemctl start caddy

# Access admin dashboard
# https://your-domain.com/admin
```

### First-Time Setup

1. Access the admin dashboard
2. Create the first admin user via the setup wizard
3. Configure system settings
4. Start adding sites

## Project Structure

```
/opt/frankenpanel/
├── control-panel/          # FastAPI backend + React frontend
│   ├── backend/            # FastAPI application
│   ├── frontend/           # React admin dashboard
│   └── static/             # Static assets
├── sites/                  # PHP site directories
│   ├── site1/
│   ├── site2/
│   └── ...
├── databases/              # MySQL/MariaDB metadata
├── backups/                # Encrypted backups
├── logs/                   # System and site logs
├── config/                 # Generated configurations
└── runtime/                # FrankenPHP workers
```

## Documentation

- [Architecture Documentation](docs/ARCHITECTURE.md)
- [API Documentation](docs/API.md)
- [Security Guide](docs/SECURITY.md)
- [Deployment Guide](docs/DEPLOYMENT.md)
- [Developer Guide](docs/DEVELOPER.md)

## License

MIT License - See LICENSE file for details

## Contributing

See CONTRIBUTING.md for guidelines.
