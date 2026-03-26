from motor.motor_asyncio import AsyncIOMotorClient
import os

#databaseconnection uniform resource locator
MONGO_URL = 'mongodb://localhost:27017'

client = AsyncIOMotorClient(MONGO_URL)

#name of database
db = client.radflow_db

#collection

users_collection = db.users
patients_collection = db.patients