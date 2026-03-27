from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.core.config import settings

_client: AsyncIOMotorClient | None = None


async def connect_db() -> None:
    global _client
    _client = AsyncIOMotorClient(settings.MONGODB_URL)
    # Verify connection
    await _client.admin.command("ping")
    print(f"[DB] Connected to MongoDB → {settings.MONGODB_DB_NAME}")


async def close_db() -> None:
    global _client
    if _client:
        _client.close()
        print("[DB] MongoDB connection closed")


def get_db() -> AsyncIOMotorDatabase:
    if _client is None:
        raise RuntimeError("Database not initialised. Call connect_db() first.")
    return _client[settings.MONGODB_DB_NAME]


# ── Collection helpers ────────────────────────────────────────────────────────
# Import get_db() in any service and call these to get typed collections

def users_col():
    return get_db()["users"]

def patients_col():
    return get_db()["patients"]

def scans_col():
    return get_db()["scans"]

def reports_col():
    return get_db()["reports"]

def templates_col():
    return get_db()["templates"]

def otps_col():
    return get_db()["otps"]

def media_col():
    return get_db()["media"]
