from fastapi import APIRouter, Depends

from src.models.presentation import PresentationResponse
from src.services import get_presentation_by_job
from src.middlewares.auth_middleware import get_current_tenant_id

router = APIRouter(prefix="/presentations", tags=["Presentations"])


@router.get("/{job_id}", response_model=PresentationResponse)
async def get_presentation(
    job_id: str,
    tenant_id: str = Depends(get_current_tenant_id)
) -> PresentationResponse:
    """
    Retrieves a finalized presentation for a specific job.
    Enforces tenant isolation and ensures the job processing status is 'completed'.
    Raises 404 if job/presentation is missing or still processing.
    """
    return await get_presentation_by_job(job_id, tenant_id)