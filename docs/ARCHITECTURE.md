# FrankenPanel Architecture Documentation

## System Architecture

### High-Level Overview

FrankenPanel is a multi-tenant platform that orchestrates PHP applications running on FrankenPHP, with each site having isolated databases and domains.

### Core Components

1. **FastAPI Backend** (`/opt/frankenpanel/control-panel/backend`)
   - Orchestration engine
   - User and permission management
   - Site lifecycle management
   - Database provisioning
   - Domain and SSL management
   - Backup/restore operations
   - Audit logging

2. **React Frontend** (`/opt/frankenpanel/control-panel/frontend`)
   - Admin dashboard
   - Site management UI
   - User management
   - Monitoring and logs
   - Backup management

3. **FrankenPHP Workers** (`/opt/frankenpanel/runtime`)
   - Isolated PHP execution per site
   - Worker process management
   - Health monitoring

4. **Caddy Reverse Proxy**
   - SSL/TLS termination
   - Domain routing
   - Load balancing (future)

5. **PostgreSQL** (Backend Metadata)
   - Users, roles, permissions
   - Sites metadata
   - Domains mapping
   - Audit logs
   - System configuration

6. **MySQL/MariaDB** (Per-Site Databases)
   - Isolated database per site
   - WordPress/Joomla databases
   - Custom application databases

## Data Flow

### Site Creation Flow

```
1. User requests site creation via API
2. Backend validates permissions
3. Backend creates site directory structure
4. Backend creates MySQL database
5. Backend generates site configuration (wp-config.php, .env)
6. Backend configures FrankenPHP worker
7. Backend updates Caddy configuration
8. Backend starts FrankenPHP worker
9. Backend reloads Caddy
10. Site is accessible via domain
```

### Request Flow

```
Client Request → Caddy → FrankenPHP Worker → PHP Application → MySQL Database
                ↓
            Admin Dashboard → FastAPI Backend → PostgreSQL
```

## Port Allocation

- **8000**: FastAPI backend (internal)
- **8081+**: FrankenPHP workers (one per site, internal)
- **80/443**: Caddy (public)

## Security Model

- Zero-trust architecture
- Encrypted secrets storage
- RBAC with fine-grained permissions
- Audit logging for all operations
- Rate limiting and IP filtering
- CSRF/XSS protection
- HTTPS enforced

## Scaling Strategy

- Horizontal scaling: Add more servers with load balancer
- Vertical scaling: Increase worker processes per site
- Database scaling: Read replicas, connection pooling
- Caching: Redis for session and metadata caching (future)

## Multi-Tenancy

- Site isolation: Separate directories, databases, workers
- User isolation: RBAC ensures users only access authorized sites
- Resource limits: Per-site CPU, memory, disk quotas (future)
