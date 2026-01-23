#!/bin/bash
#
# FrankenPanel Installation Script
# Installs all required components for FrankenPanel
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
FRANKENPANEL_ROOT="/opt/frankenpanel"
FRANKENPANEL_USER="frankenpanel"
FRANKENPANEL_GROUP="frankenpanel"
PYTHON_VERSION="3.12"

echo -e "${GREEN}=== FrankenPanel Installation Script ===${NC}"

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}Please run as root (use sudo)${NC}"
    exit 1
fi

# Detect OS
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$ID
    VER=$VERSION_ID
else
    echo -e "${RED}Cannot detect OS${NC}"
    exit 1
fi

echo -e "${GREEN}Detected OS: $OS $VER${NC}"

# Generate secure random passwords
echo -e "${YELLOW}Generating secure passwords...${NC}"
POSTGRES_PASSWORD=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-32)
MYSQL_ROOT_PASSWORD=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-32)

# Store passwords in secure file (root only, 600 permissions)
SECRETS_FILE="/root/.frankenpanel-secrets"
cat > "$SECRETS_FILE" <<SECRETS_EOF
# FrankenPanel Database Passwords
# Generated during installation on $(date)
# DO NOT SHARE OR COMMIT THIS FILE

POSTGRES_PASSWORD=$POSTGRES_PASSWORD
MYSQL_ROOT_PASSWORD=$MYSQL_ROOT_PASSWORD
SECRETS_EOF
chmod 600 "$SECRETS_FILE"
echo -e "${GREEN}Passwords stored securely in $SECRETS_FILE${NC}"

# Function to install packages
install_packages() {
    if [ "$OS" = "ubuntu" ] || [ "$OS" = "debian" ]; then
        apt-get update
        apt-get install -y \
            python3.12 python3.12-venv python3.12-dev \
            postgresql postgresql-contrib \
            mysql-server \
            curl wget git build-essential \
            ufw fail2ban \
            certbot
    elif [ "$OS" = "centos" ] || [ "$OS" = "rhel" ]; then
        yum install -y \
            python3.12 python3.12-devel \
            postgresql postgresql-server \
            mariadb-server \
            curl wget git gcc make \
            firewalld fail2ban \
            certbot
    else
        echo -e "${RED}Unsupported OS: $OS${NC}"
        exit 1
    fi
}

# Install system packages
echo -e "${YELLOW}Installing system packages...${NC}"
install_packages

# Create FrankenPanel user and group
echo -e "${YELLOW}Creating FrankenPanel user and group...${NC}"
if ! id "$FRANKENPANEL_USER" &>/dev/null; then
    useradd -r -s /bin/bash -d "$FRANKENPANEL_ROOT" -m "$FRANKENPANEL_USER"
fi

# Create directory structure
echo -e "${YELLOW}Creating directory structure...${NC}"
mkdir -p "$FRANKENPANEL_ROOT"/{control-panel/backend,control-panel/frontend,sites,databases,backups,logs,config,runtime}
chown -R "$FRANKENPANEL_USER:$FRANKENPANEL_GROUP" "$FRANKENPANEL_ROOT"
chmod 755 "$FRANKENPANEL_ROOT"

# Install PostgreSQL
echo -e "${YELLOW}Setting up PostgreSQL...${NC}"
if [ "$OS" = "ubuntu" ] || [ "$OS" = "debian" ]; then
    systemctl start postgresql
    systemctl enable postgresql
    
    # Create database and user with generated password
    sudo -u postgres psql <<EOF
CREATE DATABASE frankenpanel;
CREATE USER frankenpanel WITH PASSWORD '$POSTGRES_PASSWORD';
ALTER ROLE frankenpanel SET client_encoding TO 'utf8';
ALTER ROLE frankenpanel SET default_transaction_isolation TO 'read committed';
ALTER ROLE frankenpanel SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE frankenpanel TO frankenpanel;
EOF
fi

# Install MySQL/MariaDB
echo -e "${YELLOW}Setting up MySQL/MariaDB...${NC}"
if [ "$OS" = "ubuntu" ] || [ "$OS" = "debian" ]; then
    systemctl start mysql
    systemctl enable mysql
    
    # Wait for MySQL to be ready
    sleep 3
    
    # Set MySQL root password using generated password
    # Try mysqladmin first (works for fresh installs without password)
    mysqladmin -u root password "$MYSQL_ROOT_PASSWORD" 2>/dev/null || \
    mysql -u root <<MYSQL_SET_PWD_EOF 2>/dev/null || true
ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY '$MYSQL_ROOT_PASSWORD';
FLUSH PRIVILEGES;
MYSQL_SET_PWD_EOF
    
    # Secure MySQL installation (using generated password)
    mysql -u root -p"$MYSQL_ROOT_PASSWORD" <<MYSQL_SECURE_EOF 2>/dev/null || true
DELETE FROM mysql.user WHERE User='';
DELETE FROM mysql.user WHERE User='root' AND Host NOT IN ('localhost', '127.0.0.1', '::1');
DROP DATABASE IF EXISTS test;
DELETE FROM mysql.db WHERE Db='test' OR Db='test\\_%';
FLUSH PRIVILEGES;
MYSQL_SECURE_EOF
fi

# Install FrankenPHP
echo -e "${YELLOW}Installing FrankenPHP...${NC}"
FRANKENPHP_VERSION="1.11.1"
cd /tmp
wget -q "https://github.com/php/frankenphp/releases/download/v${FRANKENPHP_VERSION}/frankenphp-linux-x86_64" -O frankenphp
chmod +x frankenphp
mv frankenphp /usr/local/bin/frankenphp

# Install Caddy
echo -e "${YELLOW}Installing Caddy...${NC}"
if [ "$OS" = "ubuntu" ] || [ "$OS" = "debian" ]; then
    curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
    curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | tee /etc/apt/sources.list.d/caddy-stable.list
    apt-get update
    apt-get install -y caddy
fi

# Setup Python virtual environment
echo -e "${YELLOW}Setting up Python environment...${NC}"
cd "$FRANKENPANEL_ROOT/control-panel/backend"
python3.12 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Create systemd service for backend
echo -e "${YELLOW}Creating systemd service...${NC}"
cat > /etc/systemd/system/frankenpanel-backend.service <<EOF
[Unit]
Description=FrankenPanel Backend API
After=network.target postgresql.service

[Service]
Type=notify
User=$FRANKENPANEL_USER
Group=$FRANKENPANEL_GROUP
WorkingDirectory=$FRANKENPANEL_ROOT/control-panel/backend
Environment="PATH=$FRANKENPANEL_ROOT/control-panel/backend/venv/bin"
ExecStart=$FRANKENPANEL_ROOT/control-panel/backend/venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Create Caddyfile
echo -e "${YELLOW}Creating Caddyfile...${NC}"
cat > /etc/caddy/Caddyfile <<EOF
# FrankenPanel Caddyfile
# Auto-generated - do not edit manually

# Admin dashboard
admin.frankenpanel.local {
    reverse_proxy 127.0.0.1:8000
    tls internal
}

# Default site
:80 {
    respond "FrankenPanel - Multi-Site Management System"
}
EOF

# Setup firewall
echo -e "${YELLOW}Configuring firewall...${NC}"
if command -v ufw &> /dev/null; then
    ufw allow 22/tcp
    ufw allow 80/tcp
    ufw allow 443/tcp
    ufw --force enable
elif command -v firewall-cmd &> /dev/null; then
    firewall-cmd --permanent --add-service=ssh
    firewall-cmd --permanent --add-service=http
    firewall-cmd --permanent --add-service=https
    firewall-cmd --reload
fi

# Setup fail2ban
echo -e "${YELLOW}Configuring fail2ban...${NC}"
systemctl enable fail2ban
systemctl start fail2ban

# Create .env file
echo -e "${YELLOW}Creating configuration file...${NC}"
cat > "$FRANKENPANEL_ROOT/control-panel/backend/.env" <<EOF
# FrankenPanel Configuration
ENVIRONMENT=production
DEBUG=false

# Security
SECRET_KEY=$(openssl rand -hex 32)
ENCRYPTION_KEY=$(openssl rand -hex 32)

# PostgreSQL
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=frankenpanel
POSTGRES_PASSWORD=$POSTGRES_PASSWORD
POSTGRES_DB=frankenpanel

# MySQL
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_ROOT_USER=root
MYSQL_ROOT_PASSWORD=$MYSQL_ROOT_PASSWORD

# Paths
FRANKENPANEL_ROOT=$FRANKENPANEL_ROOT
SITES_DIR=$FRANKENPANEL_ROOT/sites
BACKUPS_DIR=$FRANKENPANEL_ROOT/backups
LOGS_DIR=$FRANKENPANEL_ROOT/logs
CONFIG_DIR=$FRANKENPANEL_ROOT/config
RUNTIME_DIR=$FRANKENPANEL_ROOT/runtime
EOF

chown "$FRANKENPANEL_USER:$FRANKENPANEL_GROUP" "$FRANKENPANEL_ROOT/control-panel/backend/.env"
chmod 600 "$FRANKENPANEL_ROOT/control-panel/backend/.env"

# Initialize database
echo -e "${YELLOW}Initializing database...${NC}"
cd "$FRANKENPANEL_ROOT/control-panel/backend"
source venv/bin/activate
python -c "from app.core.database import init_db; import asyncio; asyncio.run(init_db())"

# Start services
echo -e "${YELLOW}Starting services...${NC}"
systemctl daemon-reload
systemctl enable frankenpanel-backend
systemctl enable caddy
systemctl start frankenpanel-backend
systemctl start caddy

echo -e "${GREEN}=== Installation Complete ===${NC}"
echo -e "${GREEN}FrankenPanel has been installed successfully!${NC}"
echo -e ""
echo -e "${YELLOW}Important Security Information:${NC}"
echo -e "1. Database passwords have been generated and stored securely"
echo -e "2. Passwords are stored in: $SECRETS_FILE (root access only)"
echo -e "3. Passwords are also configured in: $FRANKENPANEL_ROOT/control-panel/backend/.env"
echo -e "4. Configure your domain in /etc/caddy/Caddyfile"
echo -e "5. Access admin dashboard at: http://admin.frankenpanel.local (or your configured domain)"
echo -e ""
echo -e "${YELLOW}To view passwords (root only):${NC}"
echo -e "  cat $SECRETS_FILE"
echo -e ""
echo -e "Services:"
echo -e "  - Backend: systemctl status frankenpanel-backend"
echo -e "  - Caddy: systemctl status caddy"
echo -e "  - PostgreSQL: systemctl status postgresql"
echo -e "  - MySQL: systemctl status mysql"
