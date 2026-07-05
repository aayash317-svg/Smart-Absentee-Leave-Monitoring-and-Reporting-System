"""
Security Headers Middleware (named JWTAuthMiddleware for registration in main.py).
Adds HTTP security headers to every response — CSP, X-Frame-Options, XSS, etc.
Note: JWT authentication itself is enforced at the route/dependency level via Depends().
"""
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class JWTAuthMiddleware(BaseHTTPMiddleware):
    """
    Middleware that injects security headers into every HTTP response.

    Headers applied:
    - X-Content-Type-Options   : Prevents MIME-type sniffing
    - X-Frame-Options          : Blocks clickjacking (iframe embedding)
    - X-XSS-Protection         : XSS filter for older browsers
    - Referrer-Policy          : Controls referrer info leakage
    - Content-Security-Policy  : Restricts resource loading origins
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' https://cdn.tailwindcss.com; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
            "font-src 'self' https://fonts.gstatic.com; "
            "img-src 'self' data: https:; "
            "connect-src 'self';"
        )
        return response
