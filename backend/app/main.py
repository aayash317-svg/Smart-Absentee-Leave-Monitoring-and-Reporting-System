from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from .core.config import settings
from .database.connection import connect_to_mongo, close_mongo_connection
from .api.auth import router as auth_router
from .api.student import router as student_router
from .api.coordinator import router as coordinator_router

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

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers under standard prefix
app.include_router(auth_router, prefix=settings.API_V1_STR)
app.include_router(student_router, prefix=settings.API_V1_STR)
app.include_router(coordinator_router, prefix=settings.API_V1_STR)

@app.get("/")
async def root():
    return {"message": f"Welcome to the backend of the {settings.PROJECT_NAME}"}
