from motor.motor_asyncio import AsyncIOMotorClient
from ..core.config import settings

class MongoDB:
    client: AsyncIOMotorClient = None
    db = None

db_client = MongoDB()

def connect_to_mongo():
    db_client.client = AsyncIOMotorClient(settings.MONGO_URI)
    db_client.db = db_client.client[settings.MONGO_DB_NAME]
    print(f"Successfully connected to MongoDB: {settings.MONGO_DB_NAME}")

def close_mongo_connection():
    if db_client.client:
        db_client.client.close()
        print("Closed MongoDB connection.")

def get_db():
    if db_client.db is None:
        # Fallback in case not pre-initialized (e.g. for testing)
        connect_to_mongo()
    return db_client.db
