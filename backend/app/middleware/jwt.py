"""
Security headers middleware.
Adds industry-standard HTTP security headers to every response.
These headers defend against XSS, clickjacking, MIME sniffing, and data leakage.
"""
from fastapi import Request, Response


async def security_headers_middleware(request: Request, call_next):
    """
    Injects security headers into every HTTP response.

    Headers applied:
    - X-Content-Type-Options   : Prevents MIME-type sniffing
    - X-Frame-Options          : Blocks clickjacking (iframe embedding)
    - X-XSS-Protection         : Legacy XSS filter for older browsers
    - Referrer-Policy          : Controls referrer info leakage
    - Content-Security-Policy  : Restricts resource loading origins
    """
    response: Response = await call_next(request)
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
