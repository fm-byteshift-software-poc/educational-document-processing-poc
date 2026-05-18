from fastapi import APIRouter

from src.models.auth import LoginRequest, LoginResponse
from src.services import authenticate_user

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=LoginResponse)
async def login(credentials: LoginRequest) -> LoginResponse:
    """
    Authenticates a tenant using email and password.
    Returns a JWT token and the authenticated tenant ID.
    """
    return await authenticate_user(credentials)