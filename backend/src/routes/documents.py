from fastapi import APIRouter, Depends, UploadFile, File, HTTPException

from src.models.document import DocumentUploadResponse, DocumentListResponse, DocumentListItem
from src.services import process_document_upload
from src.middlewares.auth_middleware import get_current_tenant_id
from src.repositories import get_all_documents_by_tenant

router = APIRouter(prefix="/documents", tags=["Documents"], redirect_slashes=False)


@router.post("/upload", response_model=DocumentUploadResponse, status_code=201)
async def upload_document(
    file: UploadFile = File(...),
    tenant_id: str = Depends(get_current_tenant_id)
) -> DocumentUploadResponse:
    """
    Uploads an educational document (PDF or TXT) to tenant-scoped storage.
    Validates MIME type and enforces the 5 MB size limit. 
    Returns 422 if validation fails, 201 on success.
    """
    try:
        return await process_document_upload(file, tenant_id)
    except HTTPException as e:
        raise e


@router.get("/", response_model=DocumentListResponse)
async def list_documents(
    tenant_id: str = Depends(get_current_tenant_id)
) -> DocumentListResponse:
    """
    Retrieves all documents for the authenticated tenant, ordered by upload time (newest first).
    """
    docs = await get_all_documents_by_tenant(tenant_id)
    return DocumentListResponse(documents=[DocumentListItem(**d) for d in docs])