# Site Orchestration Flow

## Site Lifecycle

### 1. Site Creation

```
User Request → API Validation → Permission Check → Site Creation
```

**Steps:**
1. User submits site creation request via API
2. Backend validates input (name, type, domain)
3. Check user permissions (site:create)
4. Generate unique slug from site name
5. Allocate next available worker port (8081, 8082, ...)
6. Create site directory: `/opt/frankenpanel/sites/{slug}`
7. Create site record in PostgreSQL
8. Create primary domain record
9. Create MySQL database (if requested)
10. Generate site configuration files:
    - WordPress: `wp-config.php`
    - Joomla: `configuration.php`
    - Custom: `.env`
11. Create FrankenPHP worker configuration
12. Update Caddy configuration
13. Start FrankenPHP worker
14. Reload Caddy
15. Return site information

### 2. Site Activation

```
Start Request → Stop Worker (if running) → Start Worker → Update Status
```

**Steps:**
1. Validate site exists and user has permission
2. Check current worker status
3. Stop worker if running
4. Start FrankenPHP worker on assigned port
5. Update site status to ACTIVE
6. Log operation

### 3. Site Deactivation

```
Stop Request → Stop Worker → Update Status
```

**Steps:**
1. Validate site exists and user has permission
2. Stop FrankenPHP worker
3. Update site status to INACTIVE
4. Log operation

### 4. Site Deletion

```
Delete Request → Stop Worker → Remove Domain → Delete Database → Remove Files → Delete Record
```

**Steps:**
1. Validate site exists and user has permission
2. Stop FrankenPHP worker
3. Remove all domains from Caddy
4. Delete MySQL database
5. Remove site directory
6. Delete site record (cascade deletes related records)
7. Log operation

## Database Lifecycle

### 1. Database Creation

```
Create Request → Generate Credentials → Create MySQL DB → Create User → Grant Privileges → Store Encrypted
```

**Steps:**
1. Generate unique database name
2. Generate database username
3. Generate secure password (32 chars)
4. Connect to MySQL as root
5. Create database with utf8mb4 charset
6. Create database user
7. Grant all privileges on database
8. Encrypt password using Fernet
9. Store in PostgreSQL
10. Return database information (password not included)

### 2. Database Password Rotation

```
Update Request → Change MySQL Password → Update Encrypted Password
```

**Steps:**
1. Generate new secure password
2. Connect to MySQL as root
3. Change user password
4. Encrypt new password
5. Update PostgreSQL record
6. Update site configuration files if needed

### 3. Database Deletion

```
Delete Request → Drop Database → Drop User → Delete Record
```

**Steps:**
1. Connect to MySQL as root
2. Drop database
3. Drop database user
4. Delete record from PostgreSQL

## Domain Lifecycle

### 1. Domain Addition

```
Add Request → Validate Domain → Create Record → Configure SSL → Update Caddy
```

**Steps:**
1. Validate domain format
2. Check domain not already in use
3. Create domain record
4. Create SSL certificate record (Caddy-managed)
5. Generate Caddyfile block
6. Append to Caddyfile
7. Reload Caddy
8. Return domain information

### 2. Domain Update

```
Update Request → Update Record → Regenerate Caddyfile → Reload Caddy
```

**Steps:**
1. Update domain record
2. Regenerate entire Caddyfile
3. Reload Caddy

### 3. Domain Removal

```
Remove Request → Remove from Caddyfile → Reload Caddy → Delete Record
```

**Steps:**
1. Regenerate Caddyfile without domain
2. Reload Caddy
3. Delete domain record

## FrankenPHP Worker Lifecycle

### 1. Worker Creation

```
Create Config → Write JSON → Set Permissions
```

**Steps:**
1. Generate worker configuration JSON
2. Write to `/opt/frankenpanel/runtime/worker_{site_id}.json`
3. Set file permissions (644)

### 2. Worker Start

```
Start Command → Launch Process → Store PID → Log Output
```

**Steps:**
1. Build FrankenPHP command with port and root directory
2. Launch process in background
3. Redirect stdout/stderr to log file
4. Store PID in `/opt/frankenpanel/runtime/worker_{site_id}.pid`
5. Return success

### 3. Worker Stop

```
Stop Request → Read PID → Send SIGTERM → Wait → Force Kill if Needed → Remove PID File
```

**Steps:**
1. Read PID from file
2. Send SIGTERM signal
3. Wait 2 seconds
4. Check if process still exists
5. Send SIGKILL if needed
6. Remove PID file
7. Return success

## Backup Lifecycle

### 1. Backup Creation

```
Create Request → Create Record → Backup Files → Backup Database → Compress → Encrypt → Update Record
```

**Steps:**
1. Create backup record (status: IN_PROGRESS)
2. Create temporary directory
3. Backup site files (tar.gz)
4. Backup database (mysqldump)
5. Create final archive
6. Compress with gzip
7. Encrypt if enabled
8. Calculate file size
9. Update record (status: COMPLETED)
10. Cleanup temporary files

### 2. Backup Restore

```
Restore Request → Validate Backup → Decrypt → Extract → Restore Files → Restore Database → Cleanup
```

**Steps:**
1. Validate backup exists and is completed
2. Decrypt backup if needed
3. Extract to temporary directory
4. Restore site files (if requested)
5. Restore database (if requested)
6. Cleanup temporary files
7. Log operation

## Multi-Site Scaling

### Port Allocation
- Worker ports start at 8081
- Each new site gets next available port
- Maximum 1000 sites (ports 8081-9080)
- Ports are tracked in PostgreSQL

### Resource Isolation
- Each site has separate directory
- Each site has separate database
- Each site has separate FrankenPHP worker
- Each site has separate log files

### Load Distribution
- Caddy routes requests to appropriate worker
- Workers run independently
- No shared state between sites
- Horizontal scaling: add more servers
