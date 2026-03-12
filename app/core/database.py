import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("DB_NAME", "adaptive_engine")

client: AsyncIOMotorClient = None


async def connect_db():
    global client
    try:
        client = AsyncIOMotorClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        db = client[DB_NAME]

        # Test connection with a simple ping
        await client.admin.command("ping")

        # Indexes for query performance
        await db["user_sessions"].create_index("session_id", unique=True)
        await db["questions"].create_index("question_id", unique=True)
        await db["questions"].create_index("difficulty")   # for range queries
        await db["questions"].create_index("topic")        # for topic filtering

        print(f"✅ Connected to MongoDB: {DB_NAME} (indexes ensured)")
    except Exception as e:
        print(f"⚠️  MongoDB connection failed: {e}")
        print("   API will still start, but database operations may fail.")
        print("   Please verify your MONGO_URI and network connectivity.")


async def disconnect_db():
    global client
    if client:
        client.close()
        print("🔌 Disconnected from MongoDB")


def get_db():
    return client[DB_NAME]
