from pymongo import MongoClient
from .config import MONGO_URI, MONGO_DB_NAME

client = MongoClient(MONGO_URI)
db = client[MONGO_DB_NAME]

def get_db():
    return db
