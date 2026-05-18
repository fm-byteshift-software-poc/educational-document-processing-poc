"""Centralized router aggregation for all /api/v1 endpoints."""
from fastapi import APIRouter

from . import auth, documents, jobs, presentations, health

# Main router with the required /api/v1 prefix
api_router = APIRouter(prefix="/api/v1")

api_router.include_router(auth.router)
api_router.include_router(documents.router)
api_router.include_router(jobs.router)
api_router.include_router(presentations.router)
api_router.include_router(health.router)