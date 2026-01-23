"""
Database management service (MySQL/MariaDB)
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.database import Database, DatabaseType
from app.schemas.database import DatabaseCreate, DatabaseUpdate
from app.core.config import settings
from app.core.security import encrypt_secret, decrypt_secret
import mysql.connector
from mysql.connector import Error
import secrets
import string
from typing import Optional


class DatabaseService:
    """Service for managing MySQL/MariaDB databases"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_database(
        self,
        site_id: int,
        name: str,
        db_type: DatabaseType = DatabaseType.MYSQL,
        password: Optional[str] = None,
    ) -> Database:
        """Create a new MySQL/MariaDB database"""
        # Generate credentials if not provided
        username = f"db_{name[:20]}"  # Limit username length
        if not password:
            password = self._generate_password()
        
        # Create database and user in MySQL
        await self._create_mysql_database(name, username, password)
        
        # Store in PostgreSQL
        db_record = Database(
            name=name,
            db_type=db_type,
            site_id=site_id,
            username=username,
            encrypted_password=encrypt_secret(password),
            host=settings.MYSQL_HOST,
            port=settings.MYSQL_PORT,
        )
        
        self.db.add(db_record)
        await self.db.commit()
        await self.db.refresh(db_record)
        
        return db_record
    
    async def delete_database(self, database_id: int) -> bool:
        """Delete a database"""
        result = await self.db.execute(select(Database).where(Database.id == database_id))
        db_record = result.scalar_one_or_none()
        
        if not db_record:
            raise ValueError(f"Database {database_id} not found")
        
        # Delete from MySQL
        password = decrypt_secret(db_record.encrypted_password)
        await self._drop_mysql_database(db_record.name, db_record.username, password)
        
        # Delete from PostgreSQL
        await self.db.delete(db_record)
        await self.db.commit()
        
        return True
    
    async def update_database_password(self, database_id: int, new_password: Optional[str] = None) -> Database:
        """Update database password"""
        result = await self.db.execute(select(Database).where(Database.id == database_id))
        db_record = result.scalar_one_or_none()
        
        if not db_record:
            raise ValueError(f"Database {database_id} not found")
        
        if not new_password:
            new_password = self._generate_password()
        
        # Update password in MySQL
        old_password = decrypt_secret(db_record.encrypted_password)
        await self._change_mysql_password(db_record.username, old_password, new_password)
        
        # Update in PostgreSQL
        db_record.encrypted_password = encrypt_secret(new_password)
        await self.db.commit()
        await self.db.refresh(db_record)
        
        return db_record
    
    async def get_database(self, database_id: int) -> Optional[Database]:
        """Get a database by ID"""
        result = await self.db.execute(select(Database).where(Database.id == database_id))
        return result.scalar_one_or_none()
    
    async def list_databases(self, site_id: Optional[int] = None) -> list[Database]:
        """List databases, optionally filtered by site"""
        query = select(Database)
        if site_id:
            query = query.where(Database.site_id == site_id)
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    def _decrypt_password(self, encrypted_password: str) -> str:
        """Decrypt database password (internal use)"""
        return decrypt_secret(encrypted_password)
    
    async def _create_mysql_database(self, db_name: str, username: str, password: str):
        """Create database and user in MySQL/MariaDB"""
        connection = None
        try:
            # Connect as root
            connection = mysql.connector.connect(
                host=settings.MYSQL_HOST,
                port=settings.MYSQL_PORT,
                user=settings.MYSQL_ROOT_USER,
                password=settings.MYSQL_ROOT_PASSWORD,
                unix_socket=settings.MYSQL_SOCKET,
            )
            
            cursor = connection.cursor()
            
            # Create database
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{db_name}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            
            # Create user
            cursor.execute(f"CREATE USER IF NOT EXISTS '{username}'@'localhost' IDENTIFIED BY '{password}'")
            
            # Grant privileges
            cursor.execute(f"GRANT ALL PRIVILEGES ON `{db_name}`.* TO '{username}'@'localhost'")
            cursor.execute("FLUSH PRIVILEGES")
            
            connection.commit()
            
        except Error as e:
            raise Exception(f"Failed to create MySQL database: {e}")
        finally:
            if connection and connection.is_connected():
                cursor.close()
                connection.close()
    
    async def _drop_mysql_database(self, db_name: str, username: str, password: str):
        """Drop database and user from MySQL/MariaDB"""
        connection = None
        try:
            connection = mysql.connector.connect(
                host=settings.MYSQL_HOST,
                port=settings.MYSQL_PORT,
                user=settings.MYSQL_ROOT_USER,
                password=settings.MYSQL_ROOT_PASSWORD,
                unix_socket=settings.MYSQL_SOCKET,
            )
            
            cursor = connection.cursor()
            
            # Drop database
            cursor.execute(f"DROP DATABASE IF EXISTS `{db_name}`")
            
            # Drop user
            cursor.execute(f"DROP USER IF EXISTS '{username}'@'localhost'")
            cursor.execute("FLUSH PRIVILEGES")
            
            connection.commit()
            
        except Error as e:
            raise Exception(f"Failed to drop MySQL database: {e}")
        finally:
            if connection and connection.is_connected():
                cursor.close()
                connection.close()
    
    async def _change_mysql_password(self, username: str, old_password: str, new_password: str):
        """Change MySQL user password"""
        connection = None
        try:
            connection = mysql.connector.connect(
                host=settings.MYSQL_HOST,
                port=settings.MYSQL_PORT,
                user=settings.MYSQL_ROOT_USER,
                password=settings.MYSQL_ROOT_PASSWORD,
                unix_socket=settings.MYSQL_SOCKET,
            )
            
            cursor = connection.cursor()
            cursor.execute(f"ALTER USER '{username}'@'localhost' IDENTIFIED BY '{new_password}'")
            cursor.execute("FLUSH PRIVILEGES")
            
            connection.commit()
            
        except Error as e:
            raise Exception(f"Failed to change MySQL password: {e}")
        finally:
            if connection and connection.is_connected():
                cursor.close()
                connection.close()
    
    def _generate_password(self, length: int = 32) -> str:
        """Generate secure random password"""
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
        return ''.join(secrets.choice(alphabet) for _ in range(length))
