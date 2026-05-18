from fastapi import HTTPException


class NotFoundException(HTTPException):
    """Raised when a requested resource does not exist."""
    def __init__(self, detail: str = "Resource not found"):
        super().__init__(status_code=404, detail=detail)


class BadRequestException(HTTPException):
    """Raised when the client sends an invalid or malformed request."""
    def __init__(self, detail: str = "Bad request"):
        super().__init__(status_code=400, detail=detail)


class UnauthorizedException(HTTPException):
    """Raised when authentication fails or provided credentials are invalid."""
    def __init__(self, detail: str = "Invalid credentials"):
        super().__init__(status_code=401, detail=detail)


class ForbiddenException(HTTPException):
    """Raised when the authenticated tenant lacks permission for this resource."""
    def __init__(self, detail: str = "Access forbidden"):
        super().__init__(status_code=403, detail=detail)