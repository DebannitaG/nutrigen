from motor.motor_asyncio import AsyncIOMotorClient
from utils.config import get_settings

settings = get_settings()

client = AsyncIOMotorClient(settings.mongodb_url)
db = client[settings.database_name]

users_collection = db["users"]
feedback_collection = db["feedback"]

async def get_database():
    return db