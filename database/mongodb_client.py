import os
import logging
from pymongo import MongoClient
from dotenv import load_dotenv
import re
import time

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
            # Check if date is properly formatted
            date_str = deadline_data.get("date_str", "")
            
            # Ensure we have a properly formatted YYYY-MM-DD date
            if not date_str or not re.match(r'^\d{4}-\d{2}-\d{2}$', date_str):
                logger.warning(f"Skipping save for event without properly formatted date: {deadline_data.get('title')}. Date: {date_str}")
                return None
                
            # Get message ID for deduplication
            message_id = deadline_data.get("message_id", "")
            if not message_id:
                logger.warning("No message_id found in event data, generating one")
                message_id = f"msg_{int(time.time())}"
                deadline_data["message_id"] = message_id
            
            # Check for existing event with same message_id
            existing = self.db.deadlines.find_one({"message_id": message_id})
            
            if existing:
                # Only update if the existing record doesn't have a properly formatted date
                existing_date = existing.get("date_str", "")
                if not re.match(r'^\d{4}-\d{2}-\d{2}$', existing_date):
                    # Update existing document with properly formatted date
                    result = self.db.deadlines.update_one(
                        {"_id": existing["_id"]},
                        {"$set": deadline_data}
                    )
                    logger.info(f"Updated existing deadline with formatted date: {existing['_id']}")
                    return str(existing["_id"])
                else:
                    # Already have a properly formatted date, skip
                    logger.info(f"Skipping duplicate save for event with message_id: {message_id}")
                    return str(existing["_id"])
            
            # No existing document found, insert new one
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
    
    def test_connection(self):
        """Test connection to MongoDB and return server info"""
        try:
            server_info = self.client.server_info()
            return server_info
        except Exception as e:
            raise Exception(f"Failed to connect to MongoDB: {e}")
    
    def check_exists_by_message_id(self, message_id):
        """Check if a deadline with the given message_id already exists
        
        Args:
            message_id (str): The message ID to check
        
        Returns:
            bool: True if the message has already been processed, False otherwise
        """
        try:
            if not message_id:
                return False
                
            # Look for any document with this message_id
            existing = self.db.deadlines.find_one({"message_id": message_id})
            return existing is not None
            
        except Exception as e:
            logger.error(f"Error checking if message exists: {e}")
            return False 