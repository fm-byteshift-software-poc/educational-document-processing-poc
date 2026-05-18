from typing import Dict, Optional
from .database import get_db


async def create_tenant(tenant: Dict[str, str]) -> None:
    """Inserts a new tenant record into the database. Used exclusively during seed phase."""
    async with get_db() as db:
        await db.execute(
            "INSERT INTO tenants (id, email, password_hash, created_at) "
            "VALUES (:id, :email, :password_hash, :created_at)",
            tenant
        )
        await db.commit()


async def get_tenant_by_email(email: str) -> Optional[Dict]:
    """Fetches a tenant by email. Returns raw data for authentication validation."""
    async with get_db() as db:
        cursor = await db.execute(
            "SELECT id, email, password_hash, created_at FROM tenants WHERE email = :email",
            {"email": email}
        )
        row = await cursor.fetchone()
        return dict(row) if row else None