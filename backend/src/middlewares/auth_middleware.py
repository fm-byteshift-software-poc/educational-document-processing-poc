from fastapi import HTTPException, status, Request
from jose import jwt
from jose.exceptions import JWTError


from src.config.settings import settings


async def get_current_tenant_id(request: Request) -> str:
    # print(f"[BACKEND AUTH] Request: {request.headers}")
    auth_header = request.headers.get("authorization") or request.headers.get("Authorization")
    # print(f"[BACKEND AUTH] Authorization header: {auth_header[:50] if auth_header else 'MISSING'}...")
    
    if not auth_header or not auth_header.startswith("Bearer "):
        # print(f"[BACKEND AUTH] Invalid header format")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = auth_header[7:]  # Remove "Bearer "
    # print(f"[BACKEND AUTH] Token preview: {token[:30]}...")
    
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        tenant_id = payload.get("sub")
        if tenant_id is None:
            # print(f"[BACKEND AUTH] Missing 'sub' claim. Payload: {payload}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token payload missing tenant ID",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return tenant_id
    except JWTError as e:
        # print(f"[BACKEND AUTH] JWT decode error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )