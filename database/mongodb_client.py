import os
import logging
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get database configuration from environment variables
MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017')
DATABASE_NAME = os.getenv('DATABASE_NAME', 'deadline_tracker')

logger = logging.getLogger('deadline-bot.database')


class MongoDBClient:
    """Client for interacting with MongoDB"""
    
    def __init__(self):
        """Initialize MongoDB client"""
        self.client = None
        self.db = None
        self.connect()
    
    def connect(self):
        """Connect to MongoDB"""
        try:
            self.client = MongoClient(MONGODB_URI)
            self.db = self.client[DATABASE_NAME]
            logger.info(f"Connected to MongoDB: {DATABASE_NAME}")
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
    
    def save_deadline(self, deadline_data):
        """Save a deadline to the database
        
        Args:
            deadline_data (dict): Deadline information
        
        Returns:
            str: ID of the inserted document or None if failed
        """
        try:
            # Check if the deadline already exists (based on message_id)
            existing = self.db.deadlines.find_one({
                "message_id": deadline_data["message_id"]
            })
            
            if existing:
                # Update existing document
                result = self.db.deadlines.update_one(
                    {"_id": existing["_id"]},
                    {"$set": deadline_data}
                )
                logger.info(f"Updated existing deadline: {existing['_id']}")
                return str(existing["_id"])
            
            # Insert new document
            result = self.db.deadlines.insert_one(deadline_data)
            logger.info(f"Saved new deadline with ID: {result.inserted_id}")
            return str(result.inserted_id)
        
        except Exception as e:
            logger.error(f"Failed to save deadline: {e}")
            return None
    
    def get_deadlines(self, limit=10, skip=0, filters=None):
        """Get deadlines from the database
        
        Args:
            limit (int): Maximum number of deadlines to return
            skip (int): Number of deadlines to skip
            filters (dict): Query filters to apply
        
        Returns:
            list: List of deadline documents
        """
        try:
            query = filters or {}
            cursor = self.db.deadlines.find(
                query
            ).sort("timestamp", -1).skip(skip).limit(limit)
            
            return list(cursor)
        
        except Exception as e:
            logger.error(f"Failed to get deadlines: {e}")
            return []
    
    def get_deadline_by_id(self, deadline_id):
        """Get a deadline by its ID
        
        Args:
            deadline_id (str): ID of the deadline
        
        Returns:
            dict: Deadline document or None if not found
        """
        try:
            from bson.objectid import ObjectId
            return self.db.deadlines.find_one({"_id": ObjectId(deadline_id)})
        except Exception as e:
            logger.error(f"Failed to get deadline by ID: {e}")
            return None
    
    def close(self):
        """Close the MongoDB connection"""
        if self.client:
            self.client.close()
            logger.info("Closed MongoDB connection") 