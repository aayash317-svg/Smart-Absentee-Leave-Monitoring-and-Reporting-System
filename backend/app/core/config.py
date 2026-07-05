import os
from pydantic import BaseModel
from typing import Dict

class Settings(BaseModel):
    PROJECT_NAME: str = "Smart Absentee Leave Monitoring & Reporting ERP"
    API_V1_STR: str = "/api"
    
    MONGO_URI: str = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
    MONGO_DB_NAME: str = os.getenv("MONGO_DB_NAME", "smart_absentee_db_v2")
    
    JWT_SECRET: str = os.getenv("JWT_SECRET", "super-secret-key-for-jwt-2026-enterprise-app")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))
    
    # Default Admin Configurable Fine weights by delay days
    DEFAULT_FINE_RULES: Dict[str, float] = {
        "0": 0.0,    # Same Day
        "1": 10.0,   # 1 Day Delay
        "2": 20.0,   # 2 Days Delay
        "3": 40.0,   # 3 Days Delay
        "4": 80.0    # 4 Days Delay
    }

settings = Settings()
