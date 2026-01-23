# FrankenPanel

<div align="center">

**A production-ready, open-source control panel for managing multiple PHP applications**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![GitHub](https://img.shields.io/github/stars/frankenpanel/frankenpanel?style=social)](https://github.com/frankenpanel/frankenpanel)

[Repository](https://github.com/frankenpanel/frankenpanel) • [Documentation](docs/) • [Contributing](CONTRIBUTING.md)

</div>

---

## What is FrankenPanel?

FrankenPanel is a **mature, enterprise-grade open-source control panel** designed for developers, agencies, and businesses who need to manage multiple PHP applications efficiently. Think of it as your own self-hosted alternative to commercial hosting panels, but with modern architecture and full control over your infrastructure.

### The Problem It Solves

Managing multiple PHP sites traditionally requires:
- Manual server configuration for each site
- Complex SSL certificate management
- Database setup and credential management
- Backup orchestration across sites
- Monitoring and logging across applications
- User access control and permissions

**FrankenPanel automates all of this** through a beautiful web interface and powerful REST API.

## Why Choose FrankenPanel?

### 🚀 **Production-Ready**
- Battle-tested architecture designed for production workloads
- Handles hundreds of sites on a single server
- Built with security and scalability in mind

### 🔒 **Secure by Default**
- Zero-trust security model
- Encrypted credential storage
- Role-based access control (RBAC)
- Complete audit logging
- Automatic SSL/TLS via Caddy

### 🎯 **Developer-Friendly**
- Modern tech stack (FastAPI, React, PostgreSQL)
- Full REST API for automation
- Easy deployment with one-command installer
- Comprehensive documentation

### 💰 **Cost-Effective**
- 100% open-source (MIT License)
- No licensing fees or subscription costs
- Self-hosted - you own your data
- No vendor lock-in

### ⚡ **High Performance**
- FrankenPHP for native PHP execution
- Isolated workers per site
- Optimized for modern PHP applications
- Built-in monitoring and logging

## Who Should Use FrankenPanel?

### 👨‍💻 **Developers & Agencies**
- Manage client websites from a single dashboard
- Deploy WordPress, Joomla, or custom PHP apps quickly
- Automate repetitive tasks via API
- Provide clients with isolated, secure environments

### 🏢 **Small to Medium Businesses**
- Self-host multiple company websites
- Control your own infrastructure
- Reduce hosting costs
- Maintain data sovereignty

### 🏗️ **Hosting Providers**
- White-label solution for your customers
- Multi-tenant architecture built-in
- Scalable to thousands of sites
- Full API for integration

### 🎓 **Educational Institutions**
- Manage multiple department websites
- Student project hosting
- Research application deployment
- Cost-effective solution for IT departments

## Key Features

### 🌐 **Multi-Site Management**
- Create and manage unlimited PHP sites
- Support for WordPress, Joomla, and custom PHP applications
- Isolated environments per site
- One-click site creation and deployment

### 🗄️ **Database Management**
- Automatic MySQL/MariaDB database creation per site
- Encrypted credential storage
- Database backup and restore
- Per-site database isolation

### 🔐 **Domain & SSL Management**
- Add domains and subdomains with ease
- Automatic SSL certificate provisioning via Caddy
- HTTP/2 and HTTP/3 support
- Custom domain routing

### 💾 **Backup & Restore**
- Automated site and database backups
- Encrypted backup storage
- One-click restore functionality
- Scheduled backup support

### 👥 **User & Permission Management**
- Role-based access control (RBAC)
- Fine-grained permissions
- Multi-user support
- Audit logging for compliance

### 📊 **Monitoring & Logging**
- Real-time site status monitoring
- Comprehensive audit logs
- System and application logging
- Performance metrics

### 🔌 **REST API**
- Full programmatic access
- Automate all operations
- Integrate with CI/CD pipelines
- Build custom tools and dashboards

## How It Works

FrankenPanel uses a modern, microservices-inspired architecture:

1. **FastAPI Backend** - Handles all orchestration, user management, and business logic
2. **React Frontend** - Beautiful, responsive admin dashboard
3. **FrankenPHP Workers** - Isolated PHP execution per site
4. **Caddy Reverse Proxy** - Automatic SSL and domain routing
5. **PostgreSQL** - Stores metadata and configuration
6. **MySQL/MariaDB** - Per-site isolated databases

Each site runs in complete isolation with its own:
- Directory structure
- Database
- PHP worker process
- Domain configuration
- SSL certificate

## Quick Start

### Prerequisites

- **Operating System**: Ubuntu 22.04+, Debian 12+, or macOS (for development)
- **Python**: 3.12 or higher
- **Access**: Root/sudo privileges for installation
- **Resources**: Minimum 2GB RAM, 2 CPU cores, 20GB disk space

### Installation

FrankenPanel can be installed with a single command:

```bash
# Clone the repository
git clone https://github.com/frankenpanel/frankenpanel.git
cd frankenpanel

# Run the automated installer
sudo bash scripts/install.sh
```

The installer will:
- ✅ Install all required dependencies
- ✅ Set up PostgreSQL and MySQL/MariaDB
- ✅ Configure FrankenPHP and Caddy
- ✅ Generate secure passwords and store them safely
- ✅ Create systemd services
- ✅ Initialize the database
- ✅ Start all services

### First-Time Setup

1. **Access the Dashboard**
   - Navigate to `http://admin.frankenpanel.local` (or your configured domain)
   - The installer will provide the exact URL

2. **Create Admin Account**
   - Use the setup wizard to create your first admin user
   - This user will have full system access

3. **Configure Settings**
   - Review system settings
   - Configure email notifications (optional)
   - Set up backup schedules

4. **Create Your First Site**
   - Click "Create Site" in the dashboard
   - Choose site type (WordPress, Joomla, or Custom PHP)
   - Add your domain
   - FrankenPanel handles the rest!

## Common Use Cases

### Use Case 1: WordPress Multi-Site Management
```
Scenario: You manage 50 WordPress sites for clients

With FrankenPanel:
- Create all sites in minutes via API
- Automatic SSL for all domains
- Scheduled backups for all sites
- Client-specific access control
- One dashboard to rule them all
```

### Use Case 2: Development Environment
```
Scenario: You need isolated dev/staging/production environments

With FrankenPanel:
- Spin up new environments instantly
- Isolated databases per environment
- Easy domain management (dev.example.com, staging.example.com)
- Quick backup/restore for testing
```

### Use Case 3: Agency Hosting
```
Scenario: Your agency hosts websites for multiple clients

With FrankenPanel:
- White-label solution
- Client-specific user accounts
- Resource isolation
- Automated deployments
- Professional SSL management
```

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
    │  - Domain/SSL management                         │
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

## Project Structure

After installation, FrankenPanel creates the following structure:

```
/opt/frankenpanel/
├── control-panel/          # FastAPI backend + React frontend
│   ├── backend/            # FastAPI application
│   ├── frontend/           # React admin dashboard
│   └── static/             # Static assets
├── sites/                  # PHP site directories
│   ├── site1/             # Isolated site directory
│   ├── site2/
│   └── ...
├── databases/              # MySQL/MariaDB metadata
├── backups/                # Encrypted backups
├── logs/                   # System and site logs
├── config/                 # Generated configurations
└── runtime/                # FrankenPHP workers
```

## Documentation

Comprehensive documentation is available for all aspects of FrankenPanel:

- 📐 [Architecture Documentation](docs/ARCHITECTURE.md) - System design and components
- 🔌 [API Documentation](docs/API.md) - REST API reference
- 🔒 [Security Guide](docs/SECURITY.md) - Security best practices
- 🚀 [Deployment Guide](docs/DEPLOYMENT.md) - Production deployment
- 👨‍💻 [Developer Guide](docs/DEVELOPER.md) - Development setup
- 🔄 [Site Orchestration](docs/SITE_ORCHESTRATION.md) - Site lifecycle management

## Security

FrankenPanel is built with security as a top priority:

- ✅ Zero-trust architecture
- ✅ Encrypted credential storage
- ✅ Role-based access control (RBAC)
- ✅ Complete audit logging
- ✅ Automatic security updates
- ✅ Input validation and sanitization
- ✅ CSRF and XSS protection
- ✅ Rate limiting
- ✅ Secure password generation

All database passwords and sensitive data are encrypted and stored securely. See our [Security Guide](docs/SECURITY.md) for details.

## API Access

Everything in FrankenPanel can be automated via REST API:

```bash
# Create a new site
curl -X POST https://your-domain.com/api/v1/sites/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My WordPress Site",
    "site_type": "wordpress",
    "domain": "example.com",
    "php_version": "8.2"
  }'

# List all sites
curl https://your-domain.com/api/v1/sites/ \
  -H "Authorization: Bearer YOUR_TOKEN"

# Create backup
curl -X POST https://your-domain.com/api/v1/backups/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"site_id": 1, "backup_type": "full"}'
```

See [API Documentation](docs/API.md) for complete API reference.

## Comparison with Other Solutions

| Feature | FrankenPanel | cPanel | Plesk | VestaCP |
|---------|-------------|--------|-------|---------|
| Open Source | ✅ MIT License | ❌ Commercial | ❌ Commercial | ✅ GPL |
| Modern Stack | ✅ FastAPI/React | ❌ Legacy | ❌ Legacy | ❌ Legacy |
| API-First | ✅ Full REST API | ⚠️ Limited | ⚠️ Limited | ⚠️ Limited |
| FrankenPHP | ✅ Native | ❌ Traditional | ❌ Traditional | ❌ Traditional |
| Self-Hosted | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes |
| Cost | ✅ Free | ❌ Paid | ❌ Paid | ✅ Free |
| Modern UI | ✅ React SPA | ❌ Legacy | ⚠️ Modern | ❌ Legacy |

## Roadmap

FrankenPanel is actively developed. Upcoming features:

- [ ] File manager in web interface
- [ ] Terminal access via web
- [ ] Resource quotas per site
- [ ] Email management
- [ ] DNS management
- [ ] Multi-server support
- [ ] Redis caching
- [ ] CDN integration
- [ ] Monitoring dashboards
- [ ] Mobile app

## Contributing

FrankenPanel is open-source and welcomes contributions! Whether you're fixing bugs, adding features, or improving documentation, your help is appreciated.

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on how to contribute.

## Support

- 📖 [Documentation](docs/) - Comprehensive guides
- 🐛 [GitHub Issues](https://github.com/frankenpanel/frankenpanel/issues) - Report bugs or request features
- 💬 [Discussions](https://github.com/frankenpanel/frankenpanel/discussions) - Community discussions
- 📧 Email: [Add your support email if available]

## License

FrankenPanel is licensed under the [MIT License](LICENSE). This means you can:

- ✅ Use it commercially
- ✅ Modify it
- ✅ Distribute it
- ✅ Private use
- ✅ Sublicense

## Acknowledgments

FrankenPanel is built on top of amazing open-source projects:

- [FrankenPHP](https://frankenphp.dev/) - Modern PHP application server
- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework
- [React](https://react.dev/) - UI library
- [Caddy](https://caddyserver.com/) - Web server with automatic HTTPS
- [PostgreSQL](https://www.postgresql.org/) - Advanced open-source database
- [MySQL](https://www.mysql.com/) - World's most popular open-source database

## Star History

If you find FrankenPanel useful, please consider giving it a ⭐ on GitHub!

---

<div align="center">

**Made with ❤️ by the FrankenPanel community**

[Get Started](#quick-start) • [Documentation](docs/) • [Contribute](CONTRIBUTING.md) • [Report Bug](https://github.com/frankenpanel/frankenpanel/issues)

</div>
