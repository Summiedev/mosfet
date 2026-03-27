"""
Run this once to create all MongoDB indexes.
Usage:  python scripts/create_indexes.py
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import sys, os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from app.core.config import settings


async def create_indexes():
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client[settings.MONGODB_DB_NAME]

    print("Creating indexes...")

    # Users
    await db["users"].create_index("email", unique=True)
    await db["users"].create_index("phone")

    # OTPs — auto-expire documents after 1 hour using TTL index
    await db["otps"].create_index("expires_at", expireAfterSeconds=3600)
    await db["otps"].create_index("phone", unique=True)

    # Patients
    await db["patients"].create_index("created_by")
    await db["patients"].create_index("name")

    # Scans
    await db["scans"].create_index("created_by")
    await db["scans"].create_index("patient_id")
    await db["scans"].create_index("status")
    await db["scans"].create_index([("created_by", 1), ("status", 1)])
    await db["scans"].create_index([("created_by", 1), ("completed_at", -1)])

    # Reports
    await db["reports"].create_index("scan_id", unique=True)
    await db["reports"].create_index("patient_id")
    await db["reports"].create_index("created_by")
    await db["reports"].create_index("is_final")

    # Templates
    await db["templates"].create_index("created_by")
    await db["templates"].create_index("scan_type")

    client.close()
    print("All indexes created successfully.")


if __name__ == "__main__":
    asyncio.run(create_indexes())
