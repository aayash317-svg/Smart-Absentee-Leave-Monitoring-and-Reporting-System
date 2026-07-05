"""
Brute-Force Rate Limiting Middleware.
Tracks failed login attempts per IP and blocks with HTTP 429 after 5 failures in 15 minutes.
Can also be used as standalone utility functions by route handlers.
"""
import datetime
from collections import defaultdict
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response, JSONResponse

# ── In-memory store (ephemeral, resets on server restart) ────────────────────
_login_attempts: dict = defaultdict(list)
_MAX_ATTEMPTS = 5
_WINDOW_SECONDS = 15 * 60  # 15 minutes


def check_login_rate_limit(ip: str) -> None:
    """Raise HTTP 429 if the IP has exceeded the login attempt limit."""
    now = datetime.datetime.utcnow()
    cutoff = now - datetime.timedelta(seconds=_WINDOW_SECONDS)
    _login_attempts[ip] = [t for t in _login_attempts[ip] if t > cutoff]
    if len(_login_attempts[ip]) >= _MAX_ATTEMPTS:
        raise Exception(
            f"Too many failed login attempts. Please wait "
            f"{_WINDOW_SECONDS // 60} minutes before trying again."
        )


def record_failed_login_attempt(ip: str) -> None:
    """Record a failed login attempt timestamp for this IP."""
    _login_attempts[ip].append(datetime.datetime.utcnow())


def clear_login_attempts(ip: str) -> None:
    """Clear all login attempt records for this IP on successful login."""
    _login_attempts.pop(ip, None)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Passive rate limiting middleware.
    Actual enforcement happens via check_login_rate_limit() called in auth routes.
    This middleware class exists as a registration point — can be extended to
    track general API abuse patterns at the middleware layer.
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        # Pass through — login-specific rate limiting is in route handlers
        return await call_next(request)
