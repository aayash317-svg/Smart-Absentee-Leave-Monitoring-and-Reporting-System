from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from ..core.jwt import decode_token

class JWTAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        
        # Bypass authentication checks for non-API endpoints, authentication paths, and open docs
        if (
            not path.startswith("/api/") or
            path in [
                "/api/auth/login", 
                "/api/auth/register", 
                "/api/auth/forgot-password", 
                "/api/auth/reset-password", 
                "/api/auth/refresh"
            ] or
            path.startswith("/api/docs") or
            path.startswith("/api/openapi.json")
        ):
            return await call_next(request)
            
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return JSONResponse(status_code=401, content={"detail": "Authorization header missing"})
            
        try:
            token_type, token = auth_header.split(" ")
            if token_type.lower() != "bearer":
                return JSONResponse(status_code=401, content={"detail": "Bearer token required"})
        except ValueError:
            return JSONResponse(status_code=401, content={"detail": "Invalid Authorization header format"})
            
        payload = decode_token(token)
        if not payload or payload.get("type") != "access":
            return JSONResponse(status_code=401, content={"detail": "Token is invalid or expired"})
            
        # Store decoded user info in request state for downstream handler extraction
        request.state.user_id = payload.get("sub")
        request.state.user_role = payload.get("role")
        
        return await call_next(request)
