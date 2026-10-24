
import os
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")

if not MONGO_URI:
    raise ValueError("MONGO_URI is missing from .env")

client = MongoClient(
    MONGO_URI,
    serverSelectionTimeoutMS=5000
)

# Database
db = client["smart_student_hub"]

# Collections
students_collection = db["students"]
ai_chats_collection = db["ai_chats"]


def test_connection():
    client.admin.command("ping")
    print("MongoDB connected successfully!")

    print("Database:", db.name)
    print("Collections ready:")
    print("- students")
    print("- ai_chats")


if __name__ == "__main__":
    try:
        test_connection()
    except Exception as error:
        print("MongoDB connection failed:", error)
