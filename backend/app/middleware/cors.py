"""
CORS configuration module.
Provides setup_cors() to register restricted CORS middleware on the FastAPI app.
No wildcard (*) origins — only known local/production origins are permitted.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# --- SECURITY: Restricted CORS origins (no wildcard) ---
# Add your production domain here before deploying.
ALLOWED_ORIGINS = [
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "http://localhost:3000",   # dev frontend (if separate)
]


def setup_cors(app: FastAPI) -> None:
    """Register CORS middleware on the FastAPI app with restricted origins."""
    app.add_middleware(
        CORSMiddleware,
        allow_origins=ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE"],
        allow_headers=["Authorization", "Content-Type"],
    )
