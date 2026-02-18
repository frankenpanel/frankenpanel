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
PYTHON_MIN_VERSION="3.12"  # Minimum required Python version
# Panel access port (override with FRANKENPANEL_PORT=8888 before running, or edit below)
PANEL_PORT="${FRANKENPANEL_PORT:-8080}"

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
echo -e "${GREEN}Panel will be accessible on port: $PANEL_PORT (override with FRANKENPANEL_PORT=8888)${NC}"

# Resolve repo root early (before any 'cd' in the script) so path is correct
SCRIPT_PATH="${BASH_SOURCE[0]}"
if [ "${SCRIPT_PATH#/}" = "$SCRIPT_PATH" ]; then
    SCRIPT_PATH="$(pwd)/$SCRIPT_PATH"
fi
SCRIPT_DIR="$(cd "$(dirname "$SCRIPT_PATH")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

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

# Detect or install Python 3.12+
# Sets PYTHON_CMD (e.g. python3.12 or python3) for use in venv and scripts
ensure_python() {
    echo -e "${YELLOW}Checking for Python ${PYTHON_MIN_VERSION}+...${NC}"
    
    # Prefer python3.12 if available
    if command -v python3.12 &>/dev/null; then
        PYTHON_CMD="python3.12"
        echo -e "${GREEN}Using existing $(python3.12 --version)${NC}"
        return
    fi
    
    # Check default python3 version (e.g. Ubuntu 25.04 has 3.13)
    if command -v python3 &>/dev/null; then
        local ver
        ver=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")' 2>/dev/null || echo "0")
        local major minor
        major=$(echo "$ver" | cut -d. -f1)
        minor=$(echo "$ver" | cut -d. -f2)
        if [ "$major" -ge 3 ] && [ "$minor" -ge 12 ] 2>/dev/null; then
            PYTHON_CMD="python3"
            echo -e "${GREEN}Using system $(python3 --version)${NC}"
            return
        fi
    fi
    
    # On Ubuntu/Debian, install Python 3.12 from deadsnakes PPA
    if [ "$OS" = "ubuntu" ] || [ "$OS" = "debian" ]; then
        echo -e "${YELLOW}Adding deadsnakes PPA for Python 3.12...${NC}"
        apt-get update
        apt-get install -y software-properties-common
        add-apt-repository -y ppa:deadsnakes/ppa
        apt-get update
        apt-get install -y python3.12 python3.12-venv python3.12-dev
        PYTHON_CMD="python3.12"
        echo -e "${GREEN}Installed $(python3.12 --version)${NC}"
        return
    fi
    
    # CentOS/RHEL: try dnf module or SCL
    if [ "$OS" = "centos" ] || [ "$OS" = "rhel" ]; then
        if command -v python3.12 &>/dev/null; then
            PYTHON_CMD="python3.12"
            return
        fi
        echo -e "${YELLOW}Installing Python 3.12...${NC}"
        yum install -y python3.12 python3.12-devel 2>/dev/null || \
        dnf install -y python3.12 python3.12-devel 2>/dev/null || {
            echo -e "${RED}Could not install Python 3.12. Please install it manually.${NC}"
            exit 1
        }
        PYTHON_CMD="python3.12"
        return
    fi
    
    echo -e "${RED}Python ${PYTHON_MIN_VERSION}+ is required but could not be detected or installed.${NC}"
    exit 1
}

# Function to install packages (Python is installed by ensure_python)
install_packages() {
    if [ "$OS" = "ubuntu" ] || [ "$OS" = "debian" ]; then
        apt-get update
        # Ensure venv and dev packages for the Python version we use
        if [ "$PYTHON_CMD" = "python3" ]; then
            apt-get install -y python3-venv python3-dev
        elif [ "$PYTHON_CMD" = "python3.12" ]; then
            apt-get install -y python3.12-venv python3.12-dev
        fi
        apt-get install -y \
            postgresql postgresql-contrib \
            mysql-server \
            curl wget git build-essential \
            ufw fail2ban \
            certbot
    elif [ "$OS" = "centos" ] || [ "$OS" = "rhel" ]; then
        yum install -y \
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

# Ensure Python 3.12+ is available (detect system or install from PPA)
ensure_python

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
    
    # Create database and user with generated password (idempotent: always set password so re-runs stay in sync with .env)
    sudo -u postgres psql <<EOF
CREATE DATABASE frankenpanel;
CREATE USER frankenpanel WITH PASSWORD '$POSTGRES_PASSWORD';
ALTER ROLE frankenpanel WITH PASSWORD '$POSTGRES_PASSWORD';
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
    curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | gpg --batch --yes --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
    curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | tee /etc/apt/sources.list.d/caddy-stable.list
    apt-get update
    apt-get install -y caddy
fi

# Copy FrankenPanel backend from repo to installation directory
if [ ! -f "$REPO_ROOT/backend/requirements.txt" ]; then
    echo -e "${RED}Error: Could not find backend/requirements.txt.${NC}"
    echo -e "Please run this script from the FrankenPanel repository root:"
    echo -e "  git clone https://github.com/frankenpanel/frankenpanel.git"
    echo -e "  cd frankenpanel"
    echo -e "  sudo bash scripts/install.sh"
    exit 1
fi
echo -e "${YELLOW}Copying FrankenPanel backend to $FRANKENPANEL_ROOT/control-panel/backend...${NC}"
cp -a "$REPO_ROOT/backend/." "$FRANKENPANEL_ROOT/control-panel/backend/"
# Copy frontend source for later build (optional)
if [ -d "$REPO_ROOT/frontend" ]; then
    echo -e "${YELLOW}Copying frontend source...${NC}"
    cp -a "$REPO_ROOT/frontend/." "$FRANKENPANEL_ROOT/control-panel/frontend/"
fi

# Setup Python virtual environment
echo -e "${YELLOW}Setting up Python environment...${NC}"
cd "$FRANKENPANEL_ROOT/control-panel/backend"
$PYTHON_CMD -m venv venv
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
Type=simple
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

# Admin dashboard (by hostname)
admin.frankenpanel.local {
    reverse_proxy 127.0.0.1:8000
    tls internal
}

# Panel on port 80 - use http://YOUR_IP (works on most clouds without opening extra ports)
:80 {
    reverse_proxy 127.0.0.1:8000
}

# Panel on optional port - http://YOUR_IP:${PANEL_PORT} (open this port in cloud firewall if needed)
:${PANEL_PORT} {
    reverse_proxy 127.0.0.1:8000
}
EOF

# Validate and load Caddy config (restart so our config is used, not any previous default)
if command -v caddy &> /dev/null; then
    caddy validate --config /etc/caddy/Caddyfile || true
fi

# Setup firewall
echo -e "${YELLOW}Configuring firewall...${NC}"
if command -v ufw &> /dev/null; then
    ufw allow 22/tcp
    ufw allow 80/tcp
    ufw allow 443/tcp
    ufw allow "${PANEL_PORT}"/tcp
    ufw --force enable
elif command -v firewall-cmd &> /dev/null; then
    firewall-cmd --permanent --add-service=ssh
    firewall-cmd --permanent --add-service=http
    firewall-cmd --permanent --add-service=https
    firewall-cmd --permanent --add-port="${PANEL_PORT}/tcp"
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

# Ensure backend and venv are owned by frankenpanel user (for systemd service)
chown -R "$FRANKENPANEL_USER:$FRANKENPANEL_GROUP" "$FRANKENPANEL_ROOT/control-panel/backend"
[ -d "$FRANKENPANEL_ROOT/control-panel/frontend" ] && chown -R "$FRANKENPANEL_USER:$FRANKENPANEL_GROUP" "$FRANKENPANEL_ROOT/control-panel/frontend"

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
# Restart Caddy so it loads our Caddyfile (avoids keeping an old "default Caddy" config)
systemctl restart caddy

echo -e "${GREEN}=== Installation Complete ===${NC}"
echo -e "${GREEN}FrankenPanel has been installed successfully!${NC}"
echo -e ""
echo -e "${YELLOW}Important Security Information:${NC}"
echo -e "1. Database passwords have been generated and stored securely"
echo -e "2. Passwords are stored in: $SECRETS_FILE (root access only)"
echo -e "3. Passwords are also configured in: $FRANKENPANEL_ROOT/control-panel/backend/.env"
echo -e "4. Configure your domain in /etc/caddy/Caddyfile"
echo -e "5. Access admin dashboard:"
echo -e "   - http://YOUR_SERVER_IP          (port 80, try this first)"
echo -e "   - http://YOUR_SERVER_IP:${PANEL_PORT}  (port ${PANEL_PORT}; if using a cloud VPS, open this port in the cloud firewall)"
echo -e "   - http://admin.frankenpanel.local (if DNS/hosts set)"
echo -e ""
echo -e "${YELLOW}If the panel does not load: open port 80 (and ${PANEL_PORT} if used) in your cloud provider's firewall (DigitalOcean/AWS/Linode etc.).${NC}"
echo -e ""
echo -e "${YELLOW}To view passwords (root only):${NC}"
echo -e "  cat $SECRETS_FILE"
echo -e ""
echo -e "Services:"
echo -e "  - Backend: systemctl status frankenpanel-backend"
echo -e "  - Caddy: systemctl status caddy"
echo -e "  - PostgreSQL: systemctl status postgresql"
echo -e "  - MySQL: systemctl status mysql"
