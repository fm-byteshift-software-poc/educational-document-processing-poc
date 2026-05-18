import asyncio
import json
import uuid
from datetime import datetime, timezone

import aiofiles
import httpx
from pypdf import PdfReader

from src.config.settings import settings
from src.models.job import CreateJobRequest, CreateJobResponse
from src.repositories import (
    get_document_by_id,
    create_job,
    update_document_status,
    update_job_status,
    create_presentation
)
from src.utils.exceptions import BadRequestException, NotFoundException

# System prompt enforcing the 5-slide structure and JSON-only output
LLM_SYSTEM_PROMPT = (
    "You are a document processor for a secure educational platform. Convert the provided document into exactly 5 structured slides. "
    "Return ONLY a valid JSON array with no preamble, no markdown fences, no commentary. "
    "The array must have exactly 5 objects in this exact order: Overview, Key Concepts, Core Content, Practical Application, Summary. "
    "Each object must have exactly these fields: slide_number (integer 1–5), section (string, the section name), "
    "heading (string, derived from source), body (string, 2 to 4 sentences derived from source). "
    "Do not invent content not present in the source document."
)


async def create_presentation_job(doc_id: str, tenant_id: str) -> CreateJobResponse:
    """Creates a presentation job for a document, enforcing tenant isolation and status checks."""
    doc = await get_document_by_id(doc_id, tenant_id)
    if not doc:
        raise NotFoundException(detail="Document not found")

    if doc["status"] == "processing":
        raise BadRequestException(detail="Document is already being processed")

    job_id = str(uuid.uuid4())
    created_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    job_data = {
        "id": job_id,
        "tenant_id": tenant_id,
        "document_id": doc_id,
        "created_at": created_at,
        "processing_status": "queued",
        "error_message": None
    }

    await create_job(job_data)
    await update_document_status(doc_id, tenant_id, "processing")

    # Fire-and-forget background task
    asyncio.create_task(_process_document_background(job_id, tenant_id, doc_id))

    return CreateJobResponse(
        job_id=job_id,
        processing_status="queued",
        document_id=doc_id
    )


async def _process_document_background(job_id: str, tenant_id: str, doc_id: str) -> None:
    """
    Async background worker that extracts text, calls the LLM, 
    persists the presentation, and updates job/document statuses.
    """
    try:
        await update_job_status(job_id, tenant_id, "processing")

        doc = await get_document_by_id(doc_id, tenant_id)
        text_content = ""

        # Extract text based on MIME type
        if doc["mime_type"] == "application/pdf":
            reader = PdfReader(doc["stored_path"])
            text_content = "\n".join(page.extract_text() or "" for page in reader.pages)
        elif doc["mime_type"] == "text/plain":
            async with aiofiles.open(doc["stored_path"], "r", encoding="utf-8") as f:
                text_content = await f.read()

        # Call HuggingFace Inference API via OpenAI-compatible client
        from openai import AsyncOpenAI
        
        client = AsyncOpenAI(
            base_url="https://router.huggingface.co/v1",
            api_key=settings.HF_API_TOKEN
        )
        
        try:
            completion = await client.chat.completions.create(
                model="meta-llama/Llama-3.1-8B-Instruct:cerebras",
                messages=[
                    {"role": "system", "content": LLM_SYSTEM_PROMPT},
                    {"role": "user", "content": text_content}
                ],
                max_tokens=1500,
            )
            raw_json = completion.choices[0].message.content
        finally:
            await client.close()

        # Validate and parse LLM output
        slides_data = json.loads(raw_json)
        if not isinstance(slides_data, list) or len(slides_data) != 5:
            raise ValueError("LLM returned an invalid slide structure")


        # Persist presentation
        pres_id = str(uuid.uuid4())
        generated_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        presentation_data = {
            "id": pres_id,
            "tenant_id": tenant_id,
            "job_id": job_id,
            "source_document_id": doc_id,
            "presentation_version": 1,
            "title": slides_data[0]["heading"],
            "slides": json.dumps(slides_data),
            "generated_at": generated_at
        }

        await create_presentation(presentation_data)
        await update_job_status(job_id, tenant_id, "completed")
        await update_document_status(doc_id, tenant_id, "completed")

    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"[JOB {job_id}] Processing failed: {type(e).__name__}: {e}")
        
        # On any failure, mark job and document as failed
        await update_job_status(job_id, tenant_id, "failed", error_message=str(e))
        await update_document_status(doc_id, tenant_id, "failed")