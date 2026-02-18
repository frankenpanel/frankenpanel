"""
Site management service
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.site import Site, SiteType, SiteStatus
from app.models.domain import Domain, DomainType
from app.models.database import Database, DatabaseType
from app.schemas.site import SiteCreate, SiteUpdate
from app.services.database_service import DatabaseService
from app.services.domain_service import DomainService
from app.services.frankenphp_service import FrankenPHPService
from app.core.config import settings
from app.core.security import encrypt_secret
import os
import shutil
import secrets
import string
import zipfile
import subprocess
import asyncio
import tempfile
from typing import Optional
from urllib.request import urlretrieve


class SiteService:
    """Service for managing sites"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.db_service = DatabaseService(db)
        self.domain_service = DomainService(db)
        self.frankenphp_service = FrankenPHPService()
    
    async def create_site(self, site_data: SiteCreate, owner_id: int) -> Site:
        """Create a new site"""
        # Generate unique slug
        slug = self._generate_slug(site_data.name)
        
        # Get next available port
        worker_port = await self._get_next_worker_port()
        
        # Create site directory (fail if path already exists so we don't overwrite)
        site_path = os.path.join(settings.SITES_DIR, slug)
        if os.path.exists(site_path):
            raise ValueError(
                f"A site directory already exists for this name. Choose a different site name or remove the existing directory: {site_path}"
            )
        os.makedirs(site_path, mode=0o755)
        
        # Create site record
        site = Site(
            name=site_data.name,
            slug=slug,
            site_type=site_data.site_type,
            status=SiteStatus.INACTIVE,
            path=site_path,
            worker_port=worker_port,
            php_version=site_data.php_version,
            config=site_data.config or {},
            owner_id=owner_id,
            description=site_data.description,
        )
        
        self.db.add(site)
        await self.db.flush()
        
        # Create primary domain
        await self.domain_service.create_domain(
            domain=site_data.domain,
            site_id=site.id,
            domain_type=DomainType.PRIMARY,
        )
        
        # Create database if requested (required for WordPress)
        db_record = None
        if site_data.create_database or site_data.site_type == SiteType.WORDPRESS:
            db_record = await self.db_service.create_database(
                site_id=site.id,
                name=f"{slug}_db",
                db_type=DatabaseType.MYSQL,
            )
        
        # WordPress: download core first, then generate config
        if site_data.site_type == SiteType.WORDPRESS:
            await self._download_wordpress(site.path)
        # Generate site configuration files (pass primary domain for wp-config)
        await self._generate_site_config(site, primary_domain=site_data.domain)
        # WordPress: run wp core install if admin credentials provided
        if site_data.site_type == SiteType.WORDPRESS and all([
            getattr(site_data, "wp_site_title", None),
            getattr(site_data, "wp_admin_user", None),
            getattr(site_data, "wp_admin_password", None),
            getattr(site_data, "wp_admin_email", None),
        ]):
            await self._run_wordpress_install(site, site_data)
        
        # Create FrankenPHP worker configuration
        await self.frankenphp_service.create_worker_config(site)
        
        await self.db.commit()
        await self.db.refresh(site)
        
        # Start site so it's live (especially for WordPress)
        if site_data.site_type == SiteType.WORDPRESS:
            await self.frankenphp_service.start_worker(site)
            site.status = SiteStatus.ACTIVE
            await self.db.commit()
            await self.db.refresh(site)
        
        return site
    
    async def update_site(self, site_id: int, site_data: SiteUpdate) -> Site:
        """Update a site"""
        result = await self.db.execute(select(Site).where(Site.id == site_id))
        site = result.scalar_one_or_none()
        
        if not site:
            raise ValueError(f"Site {site_id} not found")
        
        if site_data.name:
            site.name = site_data.name
        if site_data.description is not None:
            site.description = site_data.description
        if site_data.php_version:
            site.php_version = site_data.php_version
        if site_data.config:
            site.config.update(site_data.config)
        
        from sqlalchemy.sql import func
        site.updated_at = func.now()
        await self.db.commit()
        await self.db.refresh(site)
        
        return site
    
    async def delete_site(self, site_id: int) -> bool:
        """Delete a site"""
        result = await self.db.execute(select(Site).where(Site.id == site_id))
        site = result.scalar_one_or_none()
        
        if not site:
            raise ValueError(f"Site {site_id} not found")
        
        # Stop FrankenPHP worker
        await self.frankenphp_service.stop_worker(site)
        
        # Remove site directory
        if os.path.exists(site.path):
            shutil.rmtree(site.path)
        
        # Delete from database (cascade will handle related records)
        await self.db.delete(site)
        await self.db.commit()
        
        return True
    
    async def start_site(self, site_id: int) -> bool:
        """Start a site (start FrankenPHP worker)"""
        result = await self.db.execute(select(Site).where(Site.id == site_id))
        site = result.scalar_one_or_none()
        
        if not site:
            raise ValueError(f"Site {site_id} not found")
        
        await self.frankenphp_service.start_worker(site)
        site.status = SiteStatus.ACTIVE
        await self.db.commit()
        
        return True
    
    async def stop_site(self, site_id: int) -> bool:
        """Stop a site (stop FrankenPHP worker)"""
        result = await self.db.execute(select(Site).where(Site.id == site_id))
        site = result.scalar_one_or_none()
        
        if not site:
            raise ValueError(f"Site {site_id} not found")
        
        await self.frankenphp_service.stop_worker(site)
        site.status = SiteStatus.INACTIVE
        await self.db.commit()
        
        return True
    
    async def get_site(self, site_id: int) -> Optional[Site]:
        """Get a site by ID"""
        result = await self.db.execute(select(Site).where(Site.id == site_id))
        return result.scalar_one_or_none()
    
    async def list_sites(self, owner_id: Optional[int] = None) -> list[Site]:
        """List all sites, optionally filtered by owner"""
        query = select(Site)
        if owner_id:
            query = query.where(Site.owner_id == owner_id)
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    def _generate_slug(self, name: str) -> str:
        """Generate URL-safe slug from name"""
        import re
        slug = re.sub(r'[^a-z0-9]+', '-', name.lower())
        slug = slug.strip('-')
        return slug
    
    async def _get_next_worker_port(self) -> int:
        """Get next available worker port"""
        result = await self.db.execute(
            select(Site.worker_port).order_by(Site.worker_port.desc()).limit(1)
        )
        max_port = result.scalar_one_or_none()
        
        if max_port:
            return max_port + 1
        return settings.FRANKENPHP_WORKER_START_PORT
    
    async def _generate_site_config(self, site: Site, primary_domain: str):
        """Generate site configuration files. primary_domain is the main domain (e.g. from SiteCreate)."""
        if site.site_type == SiteType.WORDPRESS:
            await self._generate_wp_config(site, primary_domain)
        elif site.site_type == SiteType.JOOMLA:
            await self._generate_joomla_config(site)
        else:
            await self._generate_env_file(site)
    
    async def _generate_wp_config(self, site: Site, primary_domain: str):
        """Generate wp-config.php for WordPress."""
        result = await self.db.execute(
            select(Database).where(Database.site_id == site.id).limit(1)
        )
        db = result.scalar_one_or_none()
        if not db:
            return
        wp_salts = self._generate_wp_salts()
        db_password = self.db_service._decrypt_password(db.encrypted_password)
        config_content = f"""<?php
/**
 * WordPress Configuration File
 * Generated by FrankenPanel
 */

define('DB_NAME', '{db.name}');
define('DB_USER', '{db.username}');
define('DB_PASSWORD', '{db_password}');
define('DB_HOST', '{db.host}:{db.port}');
define('DB_CHARSET', 'utf8mb4');
define('DB_COLLATE', '');

{wp_salts}

define('WP_DEBUG', false);
define('WP_DEBUG_LOG', true);
define('WP_DEBUG_DISPLAY', false);

define('WP_HOME', 'https://{primary_domain}');
define('WP_SITEURL', 'https://{primary_domain}');

/* That's all, stop editing! Happy publishing. */
"""
        config_path = os.path.join(site.path, "wp-config.php")
        with open(config_path, "w") as f:
            f.write(config_content)
        os.chmod(config_path, 0o644)
    
    async def _generate_joomla_config(self, site: Site):
        """Generate configuration.php for Joomla"""
        # Similar to WordPress but for Joomla
        pass
    
    async def _generate_env_file(self, site: Site):
        """Generate .env file for custom PHP apps"""
        result = await self.db.execute(
            select(Database).where(Database.site_id == site.id).limit(1)
        )
        db = result.scalar_one_or_none()
        
        if not db:
            return
        
        env_content = f"""APP_ENV=production
APP_DEBUG=false

DB_CONNECTION=mysql
DB_HOST={db.host}
DB_PORT={db.port}
DB_DATABASE={db.name}
DB_USERNAME={db.username}
DB_PASSWORD={self.db_service._decrypt_password(db.encrypted_password)}
"""
        
        env_path = os.path.join(site.path, ".env")
        with open(env_path, "w") as f:
            f.write(env_content)
        os.chmod(env_path, 0o600)
    
    def _generate_wp_salts(self) -> str:
        """Generate WordPress security salts"""
        salts = [
            "AUTH_KEY", "SECURE_AUTH_KEY", "LOGGED_IN_KEY", "NONCE_KEY",
            "AUTH_SALT", "SECURE_AUTH_SALT", "LOGGED_IN_SALT", "NONCE_SALT"
        ]
        lines = []
        for salt in salts:
            value = secrets.token_urlsafe(64)
            lines.append(f"define('{salt}', '{value}');")
        return "\n".join(lines)

    async def _download_wordpress(self, site_path: str) -> None:
        """Download and extract WordPress latest into site_path."""
        url = "https://wordpress.org/latest.zip"
        loop = asyncio.get_event_loop()
        with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as tmp:
            tmp_path = tmp.name
        try:
            await loop.run_in_executor(None, lambda: urlretrieve(url, tmp_path))
            with zipfile.ZipFile(tmp_path, "r") as z:
                # Zip has top-level "wordpress/" folder; extract its contents into site_path
                for name in z.namelist():
                    if name.startswith("wordpress/") and not name.endswith("/"):
                        out = os.path.join(site_path, os.path.relpath(name, "wordpress"))
                        os.makedirs(os.path.dirname(out), exist_ok=True)
                        with z.open(name) as src, open(out, "wb") as dst:
                            dst.write(src.read())
                    elif name == "wordpress/":
                        continue
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

    async def _run_wordpress_install(self, site: Site, site_data: SiteCreate) -> None:
        """Run wp core install (WP-CLI) to make WordPress live. No-op if WP-CLI not found."""
        wp_cli = shutil.which("wp")
        if not wp_cli:
            return
        url = f"https://{site_data.domain}"
        proc = await asyncio.create_subprocess_exec(
            wp_cli,
            "core",
            "install",
            f"--url={url}",
            f"--title={site_data.wp_site_title or site.name}",
            f"--admin_user={site_data.wp_admin_user}",
            f"--admin_password={site_data.wp_admin_password}",
            f"--admin_email={site_data.wp_admin_email}",
            f"--path={site.path}",
            "--skip-email",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=site.path,
        )
        await proc.wait()
