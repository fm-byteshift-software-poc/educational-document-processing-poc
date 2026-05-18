import json
from src.models.presentation import PresentationResponse, Slide
from src.repositories import get_job_by_id, get_presentation_by_job_id
from src.utils.exceptions import NotFoundException


async def get_presentation_by_job(job_id: str, tenant_id: str) -> PresentationResponse:
    """
    Retrieves a finalized presentation for a given job, enforcing tenant isolation.
    Raises NotFoundException if the job does not exist, is not completed, or 
    the presentation record is missing.
    """
    # Verify job exists and belongs to the authenticated tenant
    job = await get_job_by_id(job_id, tenant_id)
    if not job:
        raise NotFoundException(detail="Job not found")

    # Only completed jobs are allowed to return presentation data
    if job["processing_status"] != "completed":
        raise NotFoundException(detail="Presentation not ready")

    # Fetch presentation record scoped to tenant
    presentation = await get_presentation_by_job_id(job_id, tenant_id)
    if not presentation:
        raise NotFoundException(detail="Presentation not found")

    # Parse stored JSON string back into structured slide objects
    slides_data = json.loads(presentation["slides"])
    slides = [Slide(**slide) for slide in slides_data]

    return PresentationResponse(
        presentation_id=presentation["id"],
        tenant_id=presentation["tenant_id"],
        title=presentation["title"],
        presentation_version=presentation["presentation_version"],
        generated_at=presentation["generated_at"],
        source_document_id=presentation["source_document_id"],
        slides=slides
    )