from fastapi import Request, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt

from src.config.settings import settings
from src.utils.exceptions import UnauthorizedException

# FastAPI dependency for extracting and validating Bearer tokens
security = HTTPBearer()


async def get_current_tenant_id(
    request: Request, 
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> str:
    """
    Extracts and validates the JWT Bearer token from the Authorization header.
    Attaches the authenticated tenant_id to request.state for downstream use.
    Raises UnauthorizedException if the token is missing, malformed, or expired.
    """
    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        tenant_id = payload.get("sub")
        if not tenant_id:
            raise UnauthorizedException(detail="Token payload missing tenant ID")
            
        # Attach tenant_id to request state for repository layer enforcement
        request.state.tenant_id = tenant_id
        return tenant_id
    except JWTError:
        raise UnauthorizedException(detail="Invalid or expired token")