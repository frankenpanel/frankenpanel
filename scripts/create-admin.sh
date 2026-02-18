#!/usr/bin/env bash
# Create or reset the FrankenPanel admin user (username: admin, password: changeme).
# Run on the server from the repo, or from the backend directory with venv.
#
# Usage:
#   sudo -u frankenpanel bash scripts/create-admin.sh
#   # or if already in backend with venv:
#   python -c "$(cat scripts/create-admin.py)"
#
# From server (default install path):
#   cd /opt/frankenpanel/control-panel/backend && source venv/bin/activate && python -c '
#   import asyncio
#   from app.core.database import AsyncSessionLocal, init_db
#   from app.models.user import User
#   from app.core.security import get_password_hash
#   from sqlalchemy import select
#
#   async def main():
#       await init_db()
#       async with AsyncSessionLocal() as db:
#           r = await db.execute(select(User).where(User.username == "admin"))
#           user = r.scalar_one_or_none()
#           if user:
#               user.hashed_password = get_password_hash("changeme")
#               user.is_active = True
#               await db.commit()
#               print("Admin password reset to: changeme")
#           else:
#               u = User(username="admin", email="admin@localhost", full_name="Administrator",
#                        hashed_password=get_password_hash("changeme"), is_active=True, is_superuser=True)
#               db.add(u)
#               await db.commit()
#               print("First admin created: username=admin, password=changeme")
#   asyncio.run(main())
#   '
set -e
BACKEND_DIR="${1:-/opt/frankenpanel/control-panel/backend}"
if [ ! -d "$BACKEND_DIR" ]; then
  echo "Backend directory not found: $BACKEND_DIR"
  echo "Usage: $0 [backend_dir]"
  exit 1
fi
cd "$BACKEND_DIR"
if [ -f venv/bin/activate ]; then
  source venv/bin/activate
fi
python -c "
import asyncio
from app.core.database import AsyncSessionLocal, init_db
from app.models.user import User
from app.core.security import get_password_hash
from sqlalchemy import select

async def main():
    await init_db()
    async with AsyncSessionLocal() as db:
        r = await db.execute(select(User).where(User.username == 'admin'))
        user = r.scalar_one_or_none()
        if user:
            user.hashed_password = get_password_hash('changeme')
            user.is_active = True
            await db.commit()
            print('Admin password reset to: changeme')
        else:
            u = User(
                username='admin',
                email='admin@localhost',
                full_name='Administrator',
                hashed_password=get_password_hash('changeme'),
                is_active=True,
                is_superuser=True,
            )
            db.add(u)
            await db.commit()
            print('First admin created: username=admin, password=changeme')

asyncio.run(main())
"
