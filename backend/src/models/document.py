from typing import List
from pydantic import BaseModel


class DocumentUploadResponse(BaseModel):
    """Response schema returned after a successful file upload."""
    document_id: str
    filename: str
    status: str
    uploaded_at: str


class DocumentListItem(BaseModel):
    """Simplified document representation for list endpoints."""
    id: str
    filename: str
    status: str
    uploaded_at: str


class DocumentListResponse(BaseModel):
    """Wrapper containing the list of documents for the authenticated tenant."""
    documents: List[DocumentListItem]