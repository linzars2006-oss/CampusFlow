"""
SmartEdu AI - MongoDB Atlas Synchronization Engine
Module: backend/api/mongo_sync.py

Provides seamless real-time syncing between Django SQLite records and the user's
MongoDB Atlas Cluster:
Cluster: mongodb+srv://linzars2006_db_user:mlGTro5lId0w30Aj@cluster0.m8kzeup.mongodb.net/?appName=Cluster0
Database: smartedu
"""

import os
import logging
from datetime import datetime
from pymongo import MongoClient
from pymongo.errors import PyMongoError

logger = logging.getLogger(__name__)

MONGO_URI = os.getenv(
    "MONGO_URI",
    "mongodb+srv://linzars2006_db_user:mlGTro5lId0w30Aj@cluster0.m8kzeup.mongodb.net/?appName=Cluster0"
)
DB_NAME = "smartedu"

_mongo_client = None
_mongo_db = None


def get_mongo_db():
    """
    Returns lazy-initialized PyMongo Database instance connected to MongoDB Atlas.
    """
    global _mongo_client, _mongo_db
    if _mongo_db is None:
        try:
            _mongo_client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=4000)
            _mongo_db = _mongo_client[DB_NAME]
            # Quick ping to verify
            _mongo_client.admin.command('ping')
            logger.info("✅ Connected to MongoDB Atlas cluster 'smartedu' database.")
        except Exception as e:
            logger.warning(f"⚠️ MongoDB Atlas connection warning: {e}")
            _mongo_db = None
    return _mongo_db


def test_atlas_connection():
    """
    Diagnostic function to test Atlas cluster connectivity and collection stats.
    """
    try:
        db = get_mongo_db()
        if db is None:
            return {"status": "error", "message": "Failed to connect to MongoDB Atlas"}
        colls = db.list_collection_names()
        return {
            "status": "connected",
            "cluster": "cluster0.m8kzeup.mongodb.net",
            "database": DB_NAME,
            "collections": colls
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}


def sync_document(collection_name, filter_query, update_data):
    """
    Upserts a document into the specified collection in MongoDB Atlas.
    """
    db = get_mongo_db()
    if db is None:
        return False
    try:
        coll = db[collection_name]
        update_data["_synced_at"] = datetime.utcnow()
        coll.update_one(filter_query, {"$set": update_data}, upsert=True)
        return True
    except PyMongoError as e:
        logger.warning(f"Atlas sync error for {collection_name}: {e}")
        return False


def sync_student_record(student):
    """
    Syncs student metadata to Atlas.
    """
    data = {
        "student_id": student.id,
        "name": student.name,
        "roll_no": student.roll_no,
        "class_name": student.class_name,
        "section": student.section,
        "prev_gpa": student.prev_gpa,
        "email": student.user.email if student.user else None
    }
    return sync_document("students", {"student_id": student.id}, data)


def sync_prediction_record(prediction):
    """
    Syncs risk prediction and top factors to Atlas.
    """
    data = {
        "prediction_id": prediction.id,
        "student_id": prediction.student.id,
        "student_name": prediction.student.name,
        "roll_no": prediction.student.roll_no,
        "subject_id": prediction.subject.id,
        "subject_name": prediction.subject.name,
        "checkpoint": prediction.checkpoint,
        "model_used": prediction.model_used,
        "risk_level": prediction.risk_level,
        "confidence_score": prediction.confidence_score,
        "top_factors": prediction.top_factors,
        "created_at": prediction.created_at
    }
    return sync_document("risk_predictions", {"prediction_id": prediction.id}, data)


def sync_snapshot_record(snapshot):
    """
    Syncs weekly longitudinal engineered snapshot to Atlas.
    """
    data = {
        "student_id": snapshot.student.id,
        "subject_id": snapshot.subject.id,
        "week_number": snapshot.week_number,
        "attendance_rate": snapshot.attendance_rate,
        "avg_score_so_far": snapshot.avg_score_so_far,
        "assignment_submission_rate": snapshot.assignment_submission_rate,
        "marks_trend": snapshot.marks_trend
    }
    return sync_document(
        "weekly_snapshots",
        {"student_id": snapshot.student.id, "subject_id": snapshot.subject.id, "week_number": snapshot.week_number},
        data
    )


def log_chat_to_atlas(student_id, question, answer, context_summary):
    """
    Persists student scoped assistant conversation logs to MongoDB Atlas.
    """
    db = get_mongo_db()
    if db is None:
        return False
    try:
        coll = db["chatbot_logs"]
        coll.insert_one({
            "student_id": student_id,
            "question": question,
            "answer": answer,
            "context_summary": context_summary,
            "timestamp": datetime.utcnow()
        })
        return True
    except Exception as e:
        logger.warning(f"Error logging chat to Atlas: {e}")
        return False
