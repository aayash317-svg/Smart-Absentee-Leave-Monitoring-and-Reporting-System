"""
CORS middleware configuration.
Restricts origins to known safe domains only — no wildcard (*).
In production, update ALLOWED_ORIGINS with your deployed domain.
"""
from fastapi.middleware.cors import CORSMiddleware

# --- SECURITY: No wildcard CORS ---
# Only these origins are permitted to call the API.
ALLOWED_ORIGINS = [
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "http://localhost:3000",   # dev frontend (if separate)
]

CORS_CONFIG = dict(
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)


def register_cors(app):
    """Register CORS middleware on the FastAPI app instance."""
    app.add_middleware(CORSMiddleware, **CORS_CONFIG)
