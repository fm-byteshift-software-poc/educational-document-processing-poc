from pydantic import BaseModel


class DocumentUploadResponse(BaseModel):
    document_id: str
    filename: str
    status: str
    uploaded_at: str


class DocumentListItem(BaseModel):
    id: str
    filename: str
    status: str
    uploaded_at: str
    job_id: str | None = None


class DocumentListResponse(BaseModel):
    documents: list[DocumentListItem]