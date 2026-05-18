from typing import Dict, List, Optional
from .database import get_db


async def create_document(document: Dict[str, str]) -> None:
    """Inserts a new document record, scoped to a specific tenant."""
    async with get_db() as db:
        await db.execute(
            "INSERT INTO documents (id, tenant_id, filename, stored_path, mime_type, uploaded_at, status) "
            "VALUES (:id, :tenant_id, :filename, :stored_path, :mime_type, :uploaded_at, :status)",
            document
        )
        await db.commit()


async def get_document_by_id(doc_id: str, tenant_id: str) -> Optional[Dict]:
    """Fetches a single document by ID, strictly enforcing tenant isolation."""
    async with get_db() as db:
        cursor = await db.execute(
            "SELECT id, tenant_id, filename, stored_path, mime_type, uploaded_at, status "
            "FROM documents WHERE id = :id AND tenant_id = :tenant_id",
            {"id": doc_id, "tenant_id": tenant_id}
        )
        row = await cursor.fetchone()
        return dict(row) if row else None


async def get_all_documents_by_tenant(tenant_id: str) -> List[Dict]:
    """Fetches all documents for a tenant, including job_id if a completed job exists."""
    async with get_db() as db:
        cursor = await db.execute(
            "SELECT d.id, d.filename, d.status, d.uploaded_at, j.id as job_id "
            "FROM documents d "
            "LEFT JOIN presentation_jobs j ON d.id = j.document_id AND j.processing_status = 'completed' "
            "WHERE d.tenant_id = :tenant_id ORDER BY d.uploaded_at DESC",
            {"tenant_id": tenant_id}
        )
        rows = await cursor.fetchall()
        return [dict(r) for r in rows]


async def update_document_status(doc_id: str, tenant_id: str, status: str) -> None:
    """Updates the processing status of a document, scoped to tenant_id."""
    async with get_db() as db:
        await db.execute(
            "UPDATE documents SET status = :status "
            "WHERE id = :id AND tenant_id = :tenant_id",
            {"id": doc_id, "tenant_id": tenant_id, "status": status}
        )
        await db.commit()