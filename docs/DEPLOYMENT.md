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

**Backend not starting:**
- Check logs: `sudo journalctl -u frankenpanel-backend -n 50`
- Verify database connection
- Check .env file permissions

**Caddy not serving sites:**
- Check Caddyfile syntax: `sudo caddy validate --config /etc/caddy/Caddyfile`
- Verify domain DNS points to server
- Check firewall rules

**FrankenPHP workers not starting:**
- Check worker logs in `/opt/frankenpanel/logs`
- Verify site directories exist
- Check port availability
