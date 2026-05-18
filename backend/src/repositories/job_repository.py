from typing import Dict, Optional
from .database import get_db


async def create_job(job_data: Dict[str, str]) -> None:
    """Inserts a new presentation job record, scoped to a specific tenant."""
    async with get_db() as db:
        await db.execute(
            "INSERT INTO presentation_jobs (id, tenant_id, document_id, created_at, processing_status, error_message) "
            "VALUES (:id, :tenant_id, :document_id, :created_at, :processing_status, :error_message)",
            job_data
        )
        await db.commit()


async def get_job_by_id(job_id: str, tenant_id: str) -> Optional[Dict]:
    """Fetches a single job by ID, strictly enforcing tenant isolation."""
    async with get_db() as db:
        cursor = await db.execute(
            "SELECT id, tenant_id, document_id, created_at, processing_status, error_message "
            "FROM presentation_jobs WHERE id = :id AND tenant_id = :tenant_id",
            {"id": job_id, "tenant_id": tenant_id}
        )
        row = await cursor.fetchone()
        return dict(row) if row else None


async def update_job_status(job_id: str, tenant_id: str, status: str, error_message: Optional[str] = None) -> None:
    """Updates the processing status and optional error message of a job, scoped to tenant_id."""
    async with get_db() as db:
        await db.execute(
            "UPDATE presentation_jobs SET processing_status = :status, error_message = :error_message "
            "WHERE id = :id AND tenant_id = :tenant_id",
            {"id": job_id, "tenant_id": tenant_id, "status": status, "error_message": error_message}
        )
        await db.commit()