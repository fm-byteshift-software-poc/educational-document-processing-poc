from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    """Schema for the login request payload."""
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    """Schema for the successful login response containing JWT and tenant ID."""
    token: str
    tenant_id: str