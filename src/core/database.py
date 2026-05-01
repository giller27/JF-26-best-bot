# src/core/database.py
from motor.motor_asyncio import AsyncIOMotorClient
from src.core.config import settings

class Database:
    client: AsyncIOMotorClient = None
    db = None

    @classmethod
    async def connect(cls):
        cls.client = AsyncIOMotorClient(settings.MONGO_URL)
        cls.db = cls.client[settings.DB_NAME]
        # Створення індексів для швидкого пошуку
        await cls.db.users.create_index("user_id", unique=True)
        await cls.db.registrations.create_index("phone")

db = Database()