import os
import sys
from dotenv import load_dotenv

# Load env variables from .env if present
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "smart_absentee_db")

# --- SECURITY FIX: Enforce strong JWT secret ---
_DEFAULT_JWT_SECRET = "super-secret-attendance-hub-key-2026"
JWT_SECRET = os.getenv("JWT_SECRET", _DEFAULT_JWT_SECRET)

if JWT_SECRET == _DEFAULT_JWT_SECRET:
    print(
        "\n[SECURITY WARNING] JWT_SECRET is set to the insecure default value.\n"
        "Please set a strong, random JWT_SECRET in your .env file before deploying.\n",
        file=sys.stderr
    )

if len(JWT_SECRET) < 32:
    print(
        "\n[SECURITY WARNING] JWT_SECRET is too short (< 32 characters).\n"
        "Use a long, random secret to protect user sessions.\n",
        file=sys.stderr
    )

JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", str(60 * 24)))  # 24 hours
