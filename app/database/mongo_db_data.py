from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv
import os
from pathlib import Path

load_dotenv(Path(os.getcwd()) / "app" / ".env")

username = os.getenv("DB_USERNAME")
password = os.getenv("DB_PASSWORD")

uri = f"mongodb+srv://{username}:{password}@cluster0.bwn8dqq.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

# Create a new client and connect to the server
client = AsyncIOMotorClient(uri, server_api=ServerApi('1'))

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(f"An error occurred: {e}")



