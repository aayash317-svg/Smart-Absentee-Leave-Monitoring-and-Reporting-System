from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from contextlib import asynccontextmanager
import logging

from .core.config import settings
from .database.connection import connect_to_mongo, close_mongo_connection
from .api.auth import router as auth_router
from .api.student import router as student_router
from .api.coordinator import router as coordinator_router
from .api.hod import router as hod_router
from .api.dean import router as dean_router
from .api.admin import router as admin_router

from .middleware.jwt import JWTAuthMiddleware
from .middleware.logging import LoggingMiddleware
from .middleware.rate_limit import RateLimitMiddleware
from .middleware.cors import setup_cors

# Configure default logging handlers
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Connect to MongoDB on startup
    connect_to_mongo()
    yield
    # Close connection on shutdown
    close_mongo_connection()

app = FastAPI(
    title=settings.PROJECT_NAME, 
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

# 1. Register logging and rate limiter middlewares (outermost)
app.add_middleware(LoggingMiddleware)
app.add_middleware(RateLimitMiddleware)

# 2. Setup CORS origins controls
setup_cors(app)

# 3. Register JWT authentication check middleware
app.add_middleware(JWTAuthMiddleware)

# Register API Routers under standard prefix /api
app.include_router(auth_router, prefix=settings.API_V1_STR)
app.include_router(student_router, prefix=settings.API_V1_STR)
app.include_router(coordinator_router, prefix=settings.API_V1_STR)
app.include_router(hod_router, prefix=settings.API_V1_STR)
app.include_router(dean_router, prefix=settings.API_V1_STR)
app.include_router(admin_router, prefix=settings.API_V1_STR)

# Mount the static frontend directory under /erp
app.mount("/erp", StaticFiles(directory="stitch_smart_absence_erp"), name="erp")

@app.get("/")
async def root_redirect():
    """Redirect requests from root to the frontend login landing page."""
    return RedirectResponse(url="/erp/login_attendance_hub/code.html")
