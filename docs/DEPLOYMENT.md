# Deployment Guide

## Production Deployment

### Prerequisites

- Ubuntu 22.04+ or Debian 12+
- Root/sudo access
- Domain name (for SSL)
- Minimum 2GB RAM, 2 CPU cores, 20GB disk

### Installation Steps

1. **Run Installation Script**
   ```bash
   sudo bash scripts/install.sh
   ```

2. **Configure Environment**
   - Edit `/opt/frankenpanel/control-panel/backend/.env`
   - Change all default passwords
   - Update SECRET_KEY and ENCRYPTION_KEY

3. **Configure Database Passwords**
   ```bash
   # PostgreSQL
   sudo -u postgres psql -c "ALTER USER frankenpanel PASSWORD 'your_secure_password';"
   
   # MySQL
   sudo mysql -e "ALTER USER 'root'@'localhost' IDENTIFIED BY 'your_secure_password';"
   ```

4. **Update Caddyfile**
   ```bash
   sudo nano /etc/caddy/Caddyfile
   ```
   Replace `admin.frankenpanel.local` with your actual domain.

5. **Build Frontend**
   ```bash
   cd /opt/frankenpanel/control-panel/frontend
   npm install
   npm run build
   ```

6. **Restart Services**
   ```bash
   sudo systemctl restart frankenpanel-backend
   sudo systemctl restart caddy
   ```

### Accessing the Dashboard

1. **Build the frontend** (if you haven’t already), so the panel UI is served:
   ```bash
   cd /opt/frankenpanel/control-panel/frontend
   npm install
   npm run build
   sudo systemctl restart frankenpanel-backend
   ```

2. **Open the dashboard** in your browser (dashboard and API use **one port**; API is internal, only the dashboard is exposed):
   - **http://YOUR_SERVER_IP:8090** (open port 8090 in your cloud firewall if needed)

3. **Create the first admin user** (no users exist after a fresh install). On the server, run once:
   ```bash
   cd /opt/frankenpanel/control-panel/backend
   source .env 2>/dev/null || true
   ./venv/bin/python -c "
   import asyncio
   from app.core.database import AsyncSessionLocal, init_db
   from app.models.user import User
   from app.core.security import get_password_hash
   async def main():
       await init_db()
       async with AsyncSessionLocal() as db:
           from sqlalchemy import select
           r = await db.execute(select(User).limit(1))
           if r.scalar_one_or_none():
               print('A user already exists. Use the login page.')
               return
           user = User(
               username='admin',
               email='admin@localhost',
               full_name='Administrator',
               hashed_password=get_password_hash('changeme'),
               is_active=True,
               is_superuser=True,
           )
           db.add(user)
           await db.commit()
           print('First admin created: username=admin, password=changeme')
           print('Log in at the dashboard and change the password immediately.')
   asyncio.run(main())
   "
   ```
   Then log in at the dashboard with **admin** / **changeme** and change the password in the UI.

### Service Management

```bash
# Backend
sudo systemctl status frankenpanel-backend
sudo systemctl restart frankenpanel-backend
sudo systemctl stop frankenpanel-backend

# Caddy
sudo systemctl status caddy
sudo systemctl restart caddy

# View logs
sudo journalctl -u frankenpanel-backend -f
sudo journalctl -u caddy -f
```

### Backup Strategy

1. **Database Backups**
   - PostgreSQL: Use `pg_dump`
   - MySQL: Use `mysqldump`
   - Schedule daily backups

2. **File Backups**
   - Backup `/opt/frankenpanel/sites` directory
   - Backup `/opt/frankenpanel/backups` directory
   - Backup configuration files

3. **Automated Backups**
   ```bash
   # Add to crontab
   0 2 * * * /opt/frankenpanel/scripts/backup.sh
   ```

### Monitoring

- Monitor system resources (CPU, memory, disk)
- Monitor service status
- Review audit logs regularly
- Set up alerts for service failures

### Scaling

- **Horizontal Scaling**: Add more servers behind load balancer
- **Vertical Scaling**: Increase server resources
- **Database Scaling**: Use read replicas for MySQL
- **Caching**: Add Redis for session and metadata caching

### Troubleshooting

**Panel not accessible (browser loads forever or connection timeout):**
- **Dashboard is on port 8090 only:** Open `http://YOUR_SERVER_IP:8090`. The API is internal (same origin); no other ports are used for the panel.
- **Cloud firewall:** Open port **8090** (or your `FRANKENPANEL_PORT`) in the cloud console (Networking → Firewall / Security Groups).
- **Local firewall:** `sudo ufw allow 8090/tcp` and `sudo ufw reload`. Check: `sudo ufw status`.
- **Caddy listening:** Run `ss -tlnp | grep 8090` to confirm Caddy is bound to the dashboard port.
- **Backend up:** `sudo systemctl status frankenpanel-backend` and `sudo systemctl status caddy` must be active.

**Default Caddy page instead of FrankenPanel:**
- Force the Caddyfile to load: `sudo caddy validate --config /etc/caddy/Caddyfile` then `sudo systemctl restart caddy`.
- Ensure the backend is running and the frontend is built: `cd /opt/frankenpanel/control-panel/frontend && npm run build`, then `sudo systemctl restart frankenpanel-backend`.

**HTTP 502 Bad Gateway on port 8090:**
- Caddy is running but the backend is not responding. Fix the backend first.
- **Check backend status:** `sudo systemctl status frankenpanel-backend`. If **inactive** or **failed**, the backend is not running.
- **Check backend logs:** `sudo journalctl -u frankenpanel-backend -n 80 --no-pager`. Look for Python tracebacks, “password authentication failed” (PostgreSQL), or missing .env/path.
- **Ensure PostgreSQL is running:** `sudo systemctl start postgresql` if needed.
- **Restart backend:** `sudo systemctl restart frankenpanel-backend`, then try `http://YOUR_SERVER_IP:8090` again.

**Backend not starting / “permission denied for schema public”:**
- Check logs: `sudo journalctl -u frankenpanel-backend -n 50`. If you see **permission denied for schema public** (PostgreSQL 15+), grant schema rights:
  ```bash
  sudo -u postgres psql -d frankenpanel -c "GRANT USAGE ON SCHEMA public TO frankenpanel; GRANT CREATE ON SCHEMA public TO frankenpanel;"
  ```
  Then restart: `sudo systemctl restart frankenpanel-backend`.
- Verify database connection and .env file permissions.

**Caddy not serving sites:**
- Check Caddyfile syntax: `sudo caddy validate --config /etc/caddy/Caddyfile`
- Verify domain DNS points to server
- Check firewall rules

**FrankenPHP workers not starting:**
- Check worker logs in `/opt/frankenpanel/logs`
- Verify site directories exist
- Check port availability
