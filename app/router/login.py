from fastapi import APIRouter, Form, HTTPException
from dotenv import load_dotenv
from app.database.mongo_db_data import client
from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
from app.operations.mongo_db import fetch_mongodb_document, update_mongodb_document, insert_mongodb_document
from pathlib import Path
import os, jwt


load_dotenv(Path(os.getcwd()) / "app" / ".env")

login_garbage = APIRouter(tags=["Admin Garbage Pinky"])

db = client[os.getenv("DB_CLIENT_ID")]
collection = db[os.getenv("DB_NAME_IMAGE")]

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = "7d9d58fb023c85aa87d93b68a2b44ddfc6d8f64aeb5c0aebed64fc71cb56a0d1"  # Change this to a strong secret
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Helper function to verify the password











