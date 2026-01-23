"""
Domain management service
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.domain import Domain, DomainType
from app.models.ssl import SSLCertificate
from app.schemas.domain import DomainCreate, DomainUpdate
from app.services.caddy_service import CaddyService
from typing import Optional


class DomainService:
    """Service for managing domains"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.caddy_service = CaddyService()
    
    async def create_domain(
        self,
        domain: str,
        site_id: int,
        domain_type: DomainType = DomainType.PRIMARY,
        ssl_enabled: bool = True,
    ) -> Domain:
        """Create a new domain"""
        # Validate domain format
        self._validate_domain(domain)
        
        # Create domain record
        domain_record = Domain(
            domain=domain,
            domain_type=domain_type,
            site_id=site_id,
            ssl_enabled=ssl_enabled,
        )
        
        self.db.add(domain_record)
        await self.db.flush()
        
        # Configure SSL if enabled
        if ssl_enabled:
            ssl_cert = await self._ensure_ssl_certificate(domain)
            domain_record.ssl_certificate_id = ssl_cert.id
        
        await self.db.commit()
        await self.db.refresh(domain_record)
        
        # Update Caddy configuration
        await self.caddy_service.add_domain(domain_record)
        
        return domain_record
    
    async def update_domain(self, domain_id: int, domain_data: DomainUpdate) -> Domain:
        """Update a domain"""
        result = await self.db.execute(select(Domain).where(Domain.id == domain_id))
        domain = result.scalar_one_or_none()
        
        if not domain:
            raise ValueError(f"Domain {domain_id} not found")
        
        if domain_data.ssl_enabled is not None:
            domain.ssl_enabled = domain_data.ssl_enabled
            if domain_data.ssl_enabled and not domain.ssl_certificate_id:
                ssl_cert = await self._ensure_ssl_certificate(domain.domain)
                domain.ssl_certificate_id = ssl_cert.id
        
        if domain_data.is_active is not None:
            domain.is_active = domain_data.is_active
        
        await self.db.commit()
        await self.db.refresh(domain)
        
        # Update Caddy configuration
        await self.caddy_service.update_domain(domain)
        
        return domain
    
    async def delete_domain(self, domain_id: int) -> bool:
        """Delete a domain"""
        result = await self.db.execute(select(Domain).where(Domain.id == domain_id))
        domain = result.scalar_one_or_none()
        
        if not domain:
            raise ValueError(f"Domain {domain_id} not found")
        
        # Remove from Caddy
        await self.caddy_service.remove_domain(domain)
        
        # Delete from database
        await self.db.delete(domain)
        await self.db.commit()
        
        return True
    
    async def get_domain(self, domain_id: int) -> Optional[Domain]:
        """Get a domain by ID"""
        result = await self.db.execute(select(Domain).where(Domain.id == domain_id))
        return result.scalar_one_or_none()
    
    async def list_domains(self, site_id: Optional[int] = None) -> list[Domain]:
        """List domains, optionally filtered by site"""
        query = select(Domain)
        if site_id:
            query = query.where(Domain.site_id == site_id)
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def _ensure_ssl_certificate(self, domain: str) -> SSLCertificate:
        """Ensure SSL certificate exists for domain"""
        result = await self.db.execute(
            select(SSLCertificate).where(SSLCertificate.domain == domain)
        )
        ssl_cert = result.scalar_one_or_none()
        
        if not ssl_cert:
            # Create new SSL certificate record (Caddy will handle actual cert)
            ssl_cert = SSLCertificate(
                domain=domain,
                caddy_managed=True,
                auto_renew=True,
                is_valid=True,
            )
            self.db.add(ssl_cert)
            await self.db.commit()
            await self.db.refresh(ssl_cert)
        
        return ssl_cert
    
    def _validate_domain(self, domain: str):
        """Validate domain format"""
        import re
        pattern = r'^([a-z0-9]+(-[a-z0-9]+)*\.)+[a-z]{2,}$'
        if not re.match(pattern, domain.lower()):
            raise ValueError(f"Invalid domain format: {domain}")
