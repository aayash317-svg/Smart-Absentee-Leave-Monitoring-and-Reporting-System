"""
Request/response logging middleware.
Logs every request with method, path, status code, and duration.
Errors are written to logs/error.log, info to logs/app.log.
"""
import time
import logging
import os
from fastapi import Request

# ── Logger setup ─────────────────────────────────────────────
LOG_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "..", "logs")
os.makedirs(LOG_DIR, exist_ok=True)

_fmt = logging.Formatter(
    "%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# App logger (INFO+) → logs/app.log
app_logger = logging.getLogger("app")
app_logger.setLevel(logging.INFO)
_app_handler = logging.FileHandler(os.path.join(LOG_DIR, "app.log"), encoding="utf-8")
_app_handler.setFormatter(_fmt)
app_logger.addHandler(_app_handler)
app_logger.addHandler(logging.StreamHandler())   # also print to console

# Error logger (ERROR+) → logs/error.log
error_logger = logging.getLogger("error")
error_logger.setLevel(logging.ERROR)
_err_handler = logging.FileHandler(os.path.join(LOG_DIR, "error.log"), encoding="utf-8")
_err_handler.setFormatter(_fmt)
error_logger.addHandler(_err_handler)


async def logging_middleware(request: Request, call_next):
    """
    Logs each request: method, path, client IP, status code, and duration.
    Errors (5xx) are additionally written to error.log.
    """
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
        f"IP={client_ip} | "
        f"STATUS={response.status_code} | "
        f"{duration}ms"
    )

    if response.status_code >= 500:
        error_logger.error(msg)
    elif response.status_code >= 400:
        app_logger.warning(msg)
    else:
        app_logger.info(msg)

    return response
