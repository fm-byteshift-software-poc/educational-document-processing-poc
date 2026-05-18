from fastapi import APIRouter, Depends

from src.models.job import CreateJobRequest, CreateJobResponse, JobResponse
from src.services import create_presentation_job
from src.middlewares.auth_middleware import get_current_tenant_id
from src.repositories import get_job_by_id
from src.utils.exceptions import NotFoundException

router = APIRouter(prefix="/jobs", tags=["Jobs"])


@router.post("/", response_model=CreateJobResponse, status_code=202)
async def create_job_endpoint(
    request: CreateJobRequest,
    tenant_id: str = Depends(get_current_tenant_id)
) -> CreateJobResponse:
    """
    Queues a document for asynchronous presentation generation.
    Returns HTTP 202 Accepted immediately. Background task handles processing.
    """
    return await create_presentation_job(request.document_id, tenant_id)


@router.get("/{job_id}", response_model=JobResponse)
async def get_job_status(
    job_id: str,
    tenant_id: str = Depends(get_current_tenant_id)
) -> JobResponse:
    """
    Retrieves the processing status of a specific presentation job.
    Enforces strict tenant isolation at the data retrieval layer.
    """
    job = await get_job_by_id(job_id, tenant_id)
    if not job:
        raise NotFoundException(detail="Job not found")

    return JobResponse(
        job_id=job["id"],
        processing_status=job["processing_status"],
        document_id=job["document_id"],
        created_at=job["created_at"],
        error_message=job.get("error_message")
    )