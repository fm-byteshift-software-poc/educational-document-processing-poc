from typing import Dict, Optional
from .database import get_db


async def create_presentation(presentation_data: Dict) -> None:
    """Inserts a new presentation record, scoped to a specific tenant."""
    async with get_db() as db:
        await db.execute(
            "INSERT INTO presentations (id, tenant_id, job_id, source_document_id, presentation_version, title, slides, generated_at) "
            "VALUES (:id, :tenant_id, :job_id, :source_document_id, :presentation_version, :title, :slides, :generated_at)",
            presentation_data
        )
        await db.commit()


async def get_presentation_by_job_id(job_id: str, tenant_id: str) -> Optional[Dict]:
    """Fetches a presentation by job ID, strictly enforcing tenant isolation."""
    async with get_db() as db:
        cursor = await db.execute(
            "SELECT id, tenant_id, job_id, source_document_id, presentation_version, title, slides, generated_at "
            "FROM presentations WHERE job_id = :job_id AND tenant_id = :tenant_id",
            {"job_id": job_id, "tenant_id": tenant_id}
        )
        row = await cursor.fetchone()
        return dict(row) if row else None