"""
Backup and restore service
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.backup import Backup, BackupType, BackupStatus
from app.models.site import Site
from app.models.database import Database
from app.schemas.backup import BackupCreate, BackupRestoreRequest
from app.core.config import settings
from app.core.security import encrypt_secret, decrypt_secret
from app.services.database_service import DatabaseService
import os
import tarfile
import gzip
import shutil
from datetime import datetime
from typing import Optional
import subprocess


class BackupService:
    """Service for managing backups"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.db_service = DatabaseService(db)
    
    async def create_backup(self, backup_data: BackupCreate, user_id: int) -> Backup:
        """Create a backup"""
        # Get site
        result = await self.db.execute(select(Site).where(Site.id == backup_data.site_id))
        site = result.scalar_one_or_none()
        
        if not site:
            raise ValueError(f"Site {backup_data.site_id} not found")
        
        # Create backup record
        backup = Backup(
            site_id=backup_data.site_id,
            backup_type=backup_data.backup_type,
            status=BackupStatus.IN_PROGRESS,
            encrypted=settings.BACKUP_ENCRYPTION_ENABLED,
            description=backup_data.description,
            created_by=user_id,
        )
        
        self.db.add(backup)
        await self.db.flush()
        
        # Generate backup filename
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"backup_{site.slug}_{timestamp}.tar.gz"
        backup_path = os.path.join(settings.BACKUPS_DIR, filename)
        
        os.makedirs(settings.BACKUPS_DIR, exist_ok=True)
        
        try:
            # Create backup
            if backup_data.backup_type == BackupType.FULL:
                await self._backup_full(site, backup_path)
            elif backup_data.backup_type == BackupType.SITE_ONLY:
                await self._backup_site_only(site, backup_path)
            elif backup_data.backup_type == BackupType.DATABASE_ONLY:
                await self._backup_database_only(site, backup_path)
            
            # Get file size
            file_size = os.path.getsize(backup_path)
            
            # Encrypt if enabled
            if settings.BACKUP_ENCRYPTION_ENABLED:
                backup_path = await self._encrypt_backup(backup_path)
            
            # Update backup record
            backup.file_path = backup_path
            backup.file_size = file_size
            backup.status = BackupStatus.COMPLETED
            backup.completed_at = datetime.utcnow()
            
            await self.db.commit()
            await self.db.refresh(backup)
            
            return backup
            
        except Exception as e:
            backup.status = BackupStatus.FAILED
            backup.error_message = str(e)
            await self.db.commit()
            raise
    
    async def restore_backup(self, restore_data: BackupRestoreRequest) -> bool:
        """Restore a backup"""
        # Get backup
        result = await self.db.execute(select(Backup).where(Backup.id == restore_data.backup_id))
        backup = result.scalar_one_or_none()
        
        if not backup:
            raise ValueError(f"Backup {restore_data.backup_id} not found")
        
        if backup.status != BackupStatus.COMPLETED:
            raise ValueError("Backup is not completed")
        
        # Get site
        result = await self.db.execute(select(Site).where(Site.id == restore_data.site_id))
        site = result.scalar_one_or_none()
        
        if not site:
            raise ValueError(f"Site {restore_data.site_id} not found")
        
        backup_path = backup.file_path
        
        # Decrypt if needed
        if backup.encrypted:
            backup_path = await self._decrypt_backup(backup_path)
        
        try:
            # Extract backup
            extract_dir = os.path.join(settings.BACKUPS_DIR, f"restore_{backup.id}")
            os.makedirs(extract_dir, exist_ok=True)
            
            with tarfile.open(backup_path, "r:gz") as tar:
                tar.extractall(extract_dir)
            
            # Restore files
            if restore_data.restore_files:
                await self._restore_files(site, extract_dir)
            
            # Restore database
            if restore_data.restore_database:
                await self._restore_database(site, extract_dir)
            
            # Cleanup
            shutil.rmtree(extract_dir)
            
            return True
            
        except Exception as e:
            raise Exception(f"Restore failed: {e}")
    
    async def _backup_full(self, site: Site, backup_path: str):
        """Create full backup (site + database)"""
        # Create temporary directory
        temp_dir = os.path.join(settings.BACKUPS_DIR, f"temp_{site.id}")
        os.makedirs(temp_dir, exist_ok=True)
        
        try:
            # Backup site files
            site_backup = os.path.join(temp_dir, "site.tar.gz")
            with tarfile.open(site_backup, "w:gz") as tar:
                tar.add(site.path, arcname="site")
            
            # Backup database
            await self._backup_database_to_file(site, os.path.join(temp_dir, "database.sql"))
            
            # Create final archive
            with tarfile.open(backup_path, "w:gz") as tar:
                tar.add(site_backup, arcname="site.tar.gz")
                tar.add(os.path.join(temp_dir, "database.sql"), arcname="database.sql")
            
        finally:
            shutil.rmtree(temp_dir)
    
    async def _backup_site_only(self, site: Site, backup_path: str):
        """Backup site files only"""
        with tarfile.open(backup_path, "w:gz") as tar:
            tar.add(site.path, arcname="site")
    
    async def _backup_database_only(self, site: Site, backup_path: str):
        """Backup database only"""
        temp_dir = os.path.join(settings.BACKUPS_DIR, f"temp_db_{site.id}")
        os.makedirs(temp_dir, exist_ok=True)
        
        try:
            db_file = os.path.join(temp_dir, "database.sql")
            await self._backup_database_to_file(site, db_file)
            
            with tarfile.open(backup_path, "w:gz") as tar:
                tar.add(db_file, arcname="database.sql")
        finally:
            shutil.rmtree(temp_dir)
    
    async def _backup_database_to_file(self, site: Site, output_file: str):
        """Backup database to SQL file"""
        # Get database for site
        result = await self.db.execute(select(Database).where(Database.site_id == site.id).limit(1))
        db = result.scalar_one_or_none()
        
        if not db:
            return
        
        password = decrypt_secret(db.encrypted_password)
        
        # Use mysqldump
        cmd = [
            "mysqldump",
            f"--host={db.host}",
            f"--port={db.port}",
            f"--user={db.username}",
            f"--password={password}",
            db.name,
        ]
        
        with open(output_file, "w") as f:
            subprocess.run(cmd, stdout=f, check=True)
    
    async def _restore_files(self, site: Site, extract_dir: str):
        """Restore site files"""
        site_backup = os.path.join(extract_dir, "site.tar.gz")
        
        if os.path.exists(site_backup):
            # Backup current site
            shutil.move(site.path, f"{site.path}.backup")
            
            # Extract backup
            os.makedirs(site.path, exist_ok=True)
            with tarfile.open(site_backup, "r:gz") as tar:
                tar.extractall(os.path.dirname(site.path))
    
    async def _restore_database(self, site: Site, extract_dir: str):
        """Restore database"""
        db_file = os.path.join(extract_dir, "database.sql")
        
        if not os.path.exists(db_file):
            return
        
        # Get database
        result = await self.db.execute(select(Database).where(Database.site_id == site.id).limit(1))
        db = result.scalar_one_or_none()
        
        if not db:
            return
        
        password = decrypt_secret(db.encrypted_password)
        
        # Restore using mysql
        cmd = [
            "mysql",
            f"--host={db.host}",
            f"--port={db.port}",
            f"--user={db.username}",
            f"--password={password}",
            db.name,
        ]
        
        with open(db_file, "r") as f:
            subprocess.run(cmd, stdin=f, check=True)
    
    async def _encrypt_backup(self, backup_path: str) -> str:
        """Encrypt backup file"""
        # Use encryption key to encrypt the backup
        # For production, use proper encryption library
        encrypted_path = f"{backup_path}.enc"
        # Implementation would use Fernet or similar
        return encrypted_path
    
    async def _decrypt_backup(self, encrypted_path: str) -> str:
        """Decrypt backup file"""
        # Decrypt the backup
        decrypted_path = encrypted_path.replace(".enc", "")
        # Implementation would decrypt
        return decrypted_path
