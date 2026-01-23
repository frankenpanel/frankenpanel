"""
Caddy reverse proxy management service
"""
from app.models.domain import Domain
from app.models.site import Site
from app.core.config import settings
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import os
import subprocess
import asyncio
from typing import Optional


class CaddyService:
    """Service for managing Caddy configuration"""
    
    def __init__(self):
        self.caddy_config_file = settings.CADDY_CONFIG_FILE
        self.caddy_bin = settings.CADDY_BIN
    
    async def add_domain(self, domain: Domain):
        """Add domain to Caddy configuration"""
        # Get site
        from app.core.database import get_db
        async for db in get_db():
            result = await db.execute(select(Site).where(Site.id == domain.site_id))
            site = result.scalar_one_or_none()
            break
        
        if not site:
            return
        
        # Generate Caddyfile block
        caddy_block = self._generate_caddy_block(domain, site)
        
        # Append to Caddyfile
        await self._append_to_caddyfile(caddy_block)
        
        # Reload Caddy
        await self._reload_caddy()
    
    async def update_domain(self, domain: Domain):
        """Update domain in Caddy configuration"""
        # Regenerate entire Caddyfile
        await self._regenerate_caddyfile()
        await self._reload_caddy()
    
    async def remove_domain(self, domain: Domain):
        """Remove domain from Caddy configuration"""
        # Regenerate Caddyfile without this domain
        await self._regenerate_caddyfile()
        await self._reload_caddy()
    
    def _generate_caddy_block(self, domain: Domain, site: Site) -> str:
        """Generate Caddyfile block for a domain"""
        lines = []
        
        # Domain line
        if domain.ssl_enabled:
            lines.append(f"{domain.domain} {{")
        else:
            lines.append(f"http://{domain.domain} {{")
        
        # Reverse proxy to FrankenPHP worker
        lines.append(f"    reverse_proxy 127.0.0.1:{site.worker_port}")
        
        # SSL configuration (Caddy handles automatically)
        if domain.ssl_enabled:
            lines.append("    tls {")
            lines.append("        on_demand")
            lines.append("    }")
        
        # Security headers
        lines.append("    header {")
        lines.append('        X-Content-Type-Options "nosniff"')
        lines.append('        X-Frame-Options "DENY"')
        lines.append('        X-XSS-Protection "1; mode=block"')
        lines.append("    }")
        
        lines.append("}")
        lines.append("")
        
        return "\n".join(lines)
    
    async def _append_to_caddyfile(self, block: str):
        """Append block to Caddyfile"""
        with open(self.caddy_config_file, "a") as f:
            f.write(block)
    
    async def _regenerate_caddyfile(self):
        """Regenerate entire Caddyfile from database"""
        # This would query all domains and regenerate the file
        # For now, we'll use a simpler append approach
        pass
    
    async def _reload_caddy(self):
        """Reload Caddy configuration"""
        try:
            # Use Caddy's API or signal to reload
            subprocess.run(
                [self.caddy_bin, "reload", "--config", self.caddy_config_file],
                check=True,
                timeout=10,
            )
        except subprocess.TimeoutExpired:
            # Fallback: restart Caddy service
            subprocess.run(["systemctl", "reload", "caddy"], check=False)
        except Exception:
            # If reload fails, try restart
            subprocess.run(["systemctl", "restart", "caddy"], check=False)
