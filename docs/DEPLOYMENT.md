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
- **Use port 80 first:** Open `http://YOUR_SERVER_IP` (no port = 80). Most cloud providers allow port 80 by default.
- **Cloud firewall:** On DigitalOcean, AWS, Linode, etc., open the panel port in the cloud console (Networking → Firewall / Security Groups). Add TCP port 80 and, if you use it, 8080 (or your `FRANKENPANEL_PORT`).
- **Local firewall:** Ensure UFW allows the port: `sudo ufw allow 80/tcp` and `sudo ufw reload` (and same for 8080 if used). Check: `sudo ufw status`.
- **Caddy listening:** On the server run `ss -tlnp | grep -E '80|8080'` to confirm Caddy is bound to the port.
- **Backend up:** `sudo systemctl status frankenpanel-backend` and `sudo systemctl status caddy` must be active.

**Default Caddy page instead of FrankenPanel (one port works, others don’t, or you see “Caddy” welcome):**
- Caddy may still be using an old config. Force our Caddyfile to load: `sudo caddy validate --config /etc/caddy/Caddyfile` then `sudo systemctl restart caddy`.
- Ensure the backend is running: `sudo systemctl status frankenpanel-backend`. If it’s down, Caddy will show 502; if you see a Caddy welcome page, the request isn’t being proxied (wrong config).
- Ensure the frontend is built so the panel UI is served: `cd /opt/frankenpanel/control-panel/frontend && npm run build`.
- For “other ports not working”: open the panel port (e.g. 8080) in the **cloud** firewall as well as UFW; try `http://YOUR_SERVER_IP` (port 80) and `http://YOUR_SERVER_IP:8080` after opening both.

**HTTP 502 Bad Gateway (e.g. on port 80 or 8080):**
- Caddy is running but the backend is not responding. Fix the backend first.
- **Check backend status:** `sudo systemctl status frankenpanel-backend`. If it is **inactive** or **failed**, the backend is not running.
- **Check backend logs:** `sudo journalctl -u frankenpanel-backend -n 80 --no-pager`. Look for Python tracebacks, “password authentication failed” (PostgreSQL), “Connection refused” (database), or “No such file” (missing .env or path).
- **Ensure PostgreSQL is running:** `sudo systemctl status postgresql` and start it if needed: `sudo systemctl start postgresql`.
- **Ensure .env exists and is readable:** `sudo ls -la /opt/frankenpanel/control-panel/backend/.env`. The service user must be able to read it (install script sets ownership).
- **Restart backend after fixing:** `sudo systemctl restart frankenpanel-backend`, then try the panel again (e.g. `http://YOUR_SERVER_IP` or `http://YOUR_SERVER_IP:8080`).

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
