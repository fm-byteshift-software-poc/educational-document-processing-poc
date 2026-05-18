from typing import List
from pydantic import BaseModel


class Slide(BaseModel):
    """Represents a single slide in the generated presentation."""
    slide_number: int
    section: str
    heading: str
    body: str


class PresentationResponse(BaseModel):
    """Response schema returned when a presentation is successfully retrieved."""
    presentation_id: str
    tenant_id: str
    title: str
    presentation_version: int
    generated_at: str
    source_document_id: str
    slides: List[Slide]