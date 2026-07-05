import time
import logging
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger("app.api")

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        try:
            response = await call_next(request)
        except Exception as e:
            process_time = (time.time() - start_time) * 1000
            logger.error(
                f"Method: {request.method} | Path: {request.url.path} | "
                f"Exception: {str(e)} | Duration: {process_time:.2f}ms | "
                f"Client: {request.client.host if request.client else 'unknown'}",
                exc_info=True
            )
            raise e
            
        process_time = (time.time() - start_time) * 1000
        logger.info(
            f"Method: {request.method} | Path: {request.url.path} | "
            f"Status: {response.status_code} | Duration: {process_time:.2f}ms | "
            f"Client: {request.client.host if request.client else 'unknown'}"
        )
        return response
