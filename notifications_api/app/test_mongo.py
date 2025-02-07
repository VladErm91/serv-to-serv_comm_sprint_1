import logging
import os

from pymongo import MongoClient

logger = logging.getLogger(__name__)


def test_mongo_connection():
    uri = os.getenv("MONGO_URL", "mongodb://mongodb:27017/notifications")
    client = MongoClient(uri)
    try:
        client.admin.command("ping")
        logger.info("Pinged your deployment. You successfully connected to MongoDB!")
    except Exception as e:
        logger.info(f"Failed to connect to MongoDB: {e}")


if __name__ == "__main__":
    test_mongo_connection()
