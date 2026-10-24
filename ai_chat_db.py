
from datetime import datetime, timezone

from bson import ObjectId
from database import client

# Use the same database as your login system.
db = client["smart_student_hub"]

# Store AI Mentor messages in this collection.
ai_chats_collection = db["ai_chats"]


def save_chat_message(student_id, role, content):
    """Save one chat message for a student."""

    if role not in ("user", "assistant"):
        raise ValueError("Invalid chat message role.")

    document = {
        "student_id": ObjectId(student_id),
        "role": role,
        "content": content,
        "created_at": datetime.now(timezone.utc),
    }

    ai_chats_collection.insert_one(document)


def get_chat_history(student_id, limit=100):
    """Load a student's recent chat messages."""

    cursor = ai_chats_collection.find(
        {"student_id": ObjectId(student_id)},
        {"_id": 0, "role": 1, "content": 1, "created_at": 1},
    ).sort("created_at", -1).limit(limit)

    messages = list(cursor)
    messages.reverse()

    return [
        {
            "role": message["role"],
            "content": message["content"],
        }
        for message in messages
    ]


def clear_chat_history(student_id):
    """Delete only the current student's chat messages."""

    result = ai_chats_collection.delete_many(
        {"student_id": ObjectId(student_id)}
    )

    return result.deleted_count
