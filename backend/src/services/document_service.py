import os
import uuid
import aiofiles
from datetime import datetime, timezone
from fastapi import UploadFile

from src.config.settings import settings
from src.models.document import DocumentUploadResponse
from src.repositories import create_document
from src.utils.exceptions import BadRequestException

# Maximum allowed file size: 5 MB
MAX_FILE_SIZE = 5 * 1024 * 1024

# Allowed MIME types for document uploads
ALLOWED_MIME_TYPES = {"application/pdf", "text/plain"}


async def process_document_upload(file: UploadFile, tenant_id: str) -> DocumentUploadResponse:
    """
    Handles document upload: validates type/size, saves to tenant-scoped storage,
    and registers the document record in the database.
    """
    # 1. Validate MIME type
    if file.content_type not in ALLOWED_MIME_TYPES:
        raise BadRequestException(detail=f"Unsupported file type: {file.content_type}")

    # 2. Read content and enforce 5 MB size limit
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise BadRequestException(detail="File size exceeds the 5 MB limit")

    # 3. Generate document ID and prepare tenant-isolated storage path
    doc_id = str(uuid.uuid4())
    storage_dir = os.path.join(settings.STORAGE_PATH, tenant_id, doc_id)
    os.makedirs(storage_dir, exist_ok=True)
    stored_path = os.path.join(storage_dir, file.filename)

    # 4. Write file asynchronously to local storage
    async with aiofiles.open(stored_path, "wb") as f:
        await f.write(content)

    # 5. Persist document metadata to database
    uploaded_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    document_data = {
        "id": doc_id,
        "tenant_id": tenant_id,
        "filename": file.filename,
        "stored_path": stored_path,
        "mime_type": file.content_type,
        "uploaded_at": uploaded_at,
        "status": "uploaded"
    }

    await create_document(document_data)

    return DocumentUploadResponse(
        document_id=doc_id,
        filename=file.filename,
        status="uploaded",
        uploaded_at=uploaded_at
    )