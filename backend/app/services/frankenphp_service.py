"""
FrankenPHP worker management service
"""
from app.models.site import Site
from app.core.config import settings
import os
import json
import subprocess
import asyncio
from typing import Optional


class FrankenPHPService:
    """Service for managing FrankenPHP workers"""
    
    def __init__(self):
        self.frankenphp_bin = settings.FRANKENPHP_BIN
        self.runtime_dir = settings.RUNTIME_DIR
    
    async def create_worker_config(self, site: Site):
        """Create FrankenPHP worker configuration"""
        config = {
            "site_id": site.id,
            "site_slug": site.slug,
            "path": site.path,
            "port": site.worker_port,
            "php_version": site.php_version,
            "worker_file": os.path.join(self.runtime_dir, f"worker_{site.id}.json"),
        }
        
        config_path = os.path.join(self.runtime_dir, f"worker_{site.id}.json")
        os.makedirs(self.runtime_dir, exist_ok=True)
        
        with open(config_path, "w") as f:
            json.dump(config, f, indent=2)
        
        os.chmod(config_path, 0o644)
    
    async def start_worker(self, site: Site) -> bool:
        """Start FrankenPHP worker for site"""
        config_path = os.path.join(self.runtime_dir, f"worker_{site.id}.json")
        
        if not os.path.exists(config_path):
            await self.create_worker_config(site)
        
        # FrankenPHP command
        # FrankenPHP runs as a worker that serves PHP files
        cmd = [
            self.frankenphp_bin,
            "worker",
            "--port", str(site.worker_port),
            "--root", site.path,
        ]
        
        # Start worker process
        log_file = os.path.join(settings.LOGS_DIR, f"frankenphp_{site.id}.log")
        os.makedirs(settings.LOGS_DIR, exist_ok=True)
        
        with open(log_file, "a") as log:
            process = subprocess.Popen(
                cmd,
                stdout=log,
                stderr=subprocess.STDOUT,
                cwd=site.path,
            )
        
        # Store PID
        pid_file = os.path.join(self.runtime_dir, f"worker_{site.id}.pid")
        with open(pid_file, "w") as f:
            f.write(str(process.pid))
        
        return True
    
    async def stop_worker(self, site: Site) -> bool:
        """Stop FrankenPHP worker for site"""
        pid_file = os.path.join(self.runtime_dir, f"worker_{site.id}.pid")
        
        if not os.path.exists(pid_file):
            return True  # Already stopped
        
        with open(pid_file, "r") as f:
            pid = int(f.read().strip())
        
        try:
            # Send SIGTERM
            os.kill(pid, 15)
            
            # Wait a bit, then force kill if needed
            await asyncio.sleep(2)
            try:
                os.kill(pid, 0)  # Check if process exists
                os.kill(pid, 9)  # Force kill
            except ProcessLookupError:
                pass  # Process already terminated
            
            # Remove PID file
            os.remove(pid_file)
            
        except ProcessLookupError:
            pass  # Process already stopped
        
        return True
    
    async def restart_worker(self, site: Site) -> bool:
        """Restart FrankenPHP worker"""
        await self.stop_worker(site)
        await asyncio.sleep(1)
        return await self.start_worker(site)
    
    async def get_worker_status(self, site: Site) -> dict:
        """Get worker status"""
        pid_file = os.path.join(self.runtime_dir, f"worker_{site.id}.pid")
        
        if not os.path.exists(pid_file):
            return {"status": "stopped", "pid": None}
        
        with open(pid_file, "r") as f:
            pid = int(f.read().strip())
        
        try:
            os.kill(pid, 0)  # Check if process exists
            return {"status": "running", "pid": pid}
        except ProcessLookupError:
            return {"status": "stopped", "pid": None}
    
    async def get_worker_logs(self, site: Site, lines: int = 100) -> list[str]:
        """Get worker logs"""
        log_file = os.path.join(settings.LOGS_DIR, f"frankenphp_{site.id}.log")
        
        if not os.path.exists(log_file):
            return []
        
        with open(log_file, "r") as f:
            all_lines = f.readlines()
            return all_lines[-lines:]
