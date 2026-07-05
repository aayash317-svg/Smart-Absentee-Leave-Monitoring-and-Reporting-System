"""
Request/Response Logging Middleware.
Logs every request with method, path, client IP, status code, and duration.
Writes to logs/app.log (info) and logs/error.log (errors).
"""
import time
import logging
import os
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

# ── Logger setup ─────────────────────────────────────────────────────────────
LOG_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "..", "logs")
os.makedirs(LOG_DIR, exist_ok=True)

_fmt = logging.Formatter(
    "%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# App logger → logs/app.log
app_logger = logging.getLogger("erp.app")
if not app_logger.handlers:
    app_logger.setLevel(logging.INFO)
    _fh = logging.FileHandler(os.path.join(LOG_DIR, "app.log"), encoding="utf-8")
    _fh.setFormatter(_fmt)
    app_logger.addHandler(_fh)
    app_logger.addHandler(logging.StreamHandler())

# Error logger → logs/error.log
error_logger = logging.getLogger("erp.error")
if not error_logger.handlers:
    error_logger.setLevel(logging.ERROR)
    _eh = logging.FileHandler(os.path.join(LOG_DIR, "error.log"), encoding="utf-8")
    _eh.setFormatter(_fmt)
    error_logger.addHandler(_eh)


class LoggingMiddleware(BaseHTTPMiddleware):
    """Logs every HTTP request with method, path, IP, status, and response time."""

    async def dispatch(self, request: Request, call_next) -> Response:
        start = time.time()
        client_ip = request.client.host if request.client else "unknown"

        try:
            response = await call_next(request)
        except Exception as exc:
            duration = round((time.time() - start) * 1000, 2)
            error_logger.error(
                f"{request.method} {request.url.path} | IP={client_ip} | "
                f"UNHANDLED ERROR: {exc} | {duration}ms"
            )
            raise

        duration = round((time.time() - start) * 1000, 2)
        msg = (
            f"{request.method} {request.url.path} | "
            f"IP={client_ip} | STATUS={response.status_code} | {duration}ms"
        )

        if response.status_code >= 500:
            error_logger.error(msg)
        elif response.status_code >= 400:
            app_logger.warning(msg)
        else:
            app_logger.info(msg)

        return response
