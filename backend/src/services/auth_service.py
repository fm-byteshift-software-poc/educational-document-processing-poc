import bcrypt
from datetime import datetime, timedelta, timezone
from jose import jwt

from src.config.settings import settings
from src.models.auth import LoginRequest, LoginResponse
from src.repositories import get_tenant_by_email
from src.utils.exceptions import UnauthorizedException


async def authenticate_user(credentials: LoginRequest) -> LoginResponse:
    """Validates email/password against the tenant database and issues a JWT."""
    tenant = await get_tenant_by_email(credentials.email)
    if not tenant or not bcrypt.checkpw(
        credentials.password.encode(), tenant["password_hash"].encode()
    ):
        raise UnauthorizedException()

    expire = datetime.now(timezone.utc) + timedelta(hours=settings.JWT_EXPIRE_HOURS)
    payload = {"sub": tenant["id"], "exp": expire}
    
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

    return LoginResponse(token=token, tenant_id=tenant["id"])