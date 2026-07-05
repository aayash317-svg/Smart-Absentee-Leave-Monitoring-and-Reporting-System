import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from collections import defaultdict
from typing import Dict, List

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, requests_per_minute: int = 60):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        # Stores access timestamps grouped by client IP: {client_ip: [timestamp1, timestamp2, ...]}
        self.client_windows: Dict[str, List[float]] = defaultdict(list)
        
    async def dispatch(self, request: Request, call_next):
        # Exclude static assets or documentation paths from rate limiting
        if not request.url.path.startswith("/api/"):
            return await call_next(request)
            
        client_ip = request.client.host if request.client else "unknown"
        now = time.time()
        
        # Remove timestamps outside the current 60-second sliding window
        self.client_windows[client_ip] = [t for t in self.client_windows[client_ip] if now - t < 60]
        
        # Enforce a stricter limit on authentication endpoints
        limit = self.requests_per_minute
        if request.url.path.startswith("/api/auth/"):
            limit = 10  # Max 10 requests per minute for login/register/reset
            
        if len(self.client_windows[client_ip]) >= limit:
            return JSONResponse(
                status_code=429,
                content={"detail": "Rate limit exceeded. Please try again after a minute."}
            )
            
        self.client_windows[client_ip].append(now)
        return await call_next(request)
