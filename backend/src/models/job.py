from typing import Optional
from pydantic import BaseModel


class CreateJobRequest(BaseModel):
    """Request schema to start processing a document into a presentation."""
    document_id: str


class CreateJobResponse(BaseModel):
    """Response schema returned immediately after a job is queued."""
    job_id: str
    processing_status: str
    document_id: str


class JobResponse(BaseModel):
    """Response schema returned when fetching the status of an existing job."""
    job_id: str
    processing_status: str
    document_id: str
    created_at: str
    error_message: Optional[str] = None