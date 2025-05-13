"""
MongoDB-based statistics manager for image classifications.
"""
import os
import time
import hashlib
from datetime import datetime, timedelta
from utils.db import get_database
from utils.imagebb import upload_image_to_imagebb
from utils.image_url_helpers import prepare_image_urls_for_frontend

class MongoDBStats:
    """
    Tracks and stores statistics for image classifications using MongoDB.
    """
    
    def __init__(self):
        """
        Initialize the MongoDB statistics tracker.
        """
        self.db = get_database()
        self.classifications = self.db.classifications
        self.statistics = self.db.statistics
        self.daily_stats = self.db.daily_stats
    
    def record_classification(self, category, confidence):
        """
        Record a new classification without image data.
        
        Args:
            category: The classified category
            confidence: The confidence score
        """
        # Get the current date
        today = datetime.now().strftime('%Y-%m-%d')
        
        # Update global statistics
        global_stats = self.statistics.find_one({"_id": "global"})
        if not global_stats:
            # Initialize global stats if not found
            global_stats = {
                "_id": "global",
                "total_classifications": 0,
                "categories": {},
                "last_updated": None
            }
        
        # Update total counts
        global_stats["total_classifications"] = global_stats.get("total_classifications", 0) + 1
        
        # Update category stats
        if category not in global_stats["categories"]:
            global_stats["categories"][category] = {
                "count": 0,
                "avg_confidence": 0
            }
        
        category_stats = global_stats["categories"][category]
        old_count = category_stats["count"]
        old_avg = category_stats["avg_confidence"]
        
        # Calculate new average confidence
        if old_count == 0:
            new_avg = confidence
        else:
            new_avg = (old_avg * old_count + confidence) / (old_count + 1)
        
        # Update category stats
        category_stats["count"] = old_count + 1
        category_stats["avg_confidence"] = new_avg
        
        # Update timestamp
        global_stats["last_updated"] = datetime.now().isoformat()
        
        # Save global stats
        self.statistics.replace_one({"_id": "global"}, global_stats, upsert=True)
        
        # Update daily stats
        daily_update_result = self.daily_stats.update_one(
            {"_id": today},
            {
                "$inc": {
                    "total": 1,
                    f"categories.{category}": 1
                },
                "$setOnInsert": {"date": today}
            },
            upsert=True
        )
    
    def record_classification_with_image(self, category, confidence, image_data, original_filename=None):
        """
        Record a new classification with the image.
        
        Args:
            category: The classified category
            confidence: The confidence score
            image_data: The image data (file-like object or bytes)
            original_filename: Original filename if available
        
        Returns:
            str: The unique ID of the recorded classification
        """
        # Generate a unique ID for this classification
        timestamp = datetime.now().isoformat()
        unique_id = f"{timestamp}-{hashlib.md5(str(time.time()).encode()).hexdigest()[:8]}"
        
        # Record basic classification data
        self.record_classification(category, confidence)
        
        try:
            # If image_data is a file-like object, read it
            if hasattr(image_data, 'read'):
                img_bytes = image_data.read()
                if hasattr(image_data, 'seek'):
                    image_data.seek(0)  # Reset file pointer
            else:
                img_bytes = image_data
            
            # Upload the image to ImageBB
            image_name = original_filename or f"{category}_{unique_id}.jpg"
            upload_result = upload_image_to_imagebb(img_bytes, name=image_name)
            
            if not upload_result:
                raise Exception("Failed to upload image to ImageBB")
            
            # Create metadata for this classification
            metadata = {
                "_id": unique_id,
                "id": unique_id,
                "timestamp": timestamp,
                "category": category,
                "confidence": confidence,
                "original_filename": original_filename or 'unknown.jpg',
                "image_url": upload_result.get('url'),
                "image_thumbnail": upload_result.get('thumb', {}).get('url'),
                "image_medium": upload_result.get('medium', {}).get('url'),
                "delete_url": upload_result.get('delete_url')
            }
            
            # Insert the classification into MongoDB
            self.classifications.insert_one(metadata)
            
            print(f"Image uploaded to ImageBB and recorded in MongoDB: {upload_result.get('url')}")
            return unique_id
            
        except Exception as e:
            print(f"Error saving image classification: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def get_classification_history(self, limit=50, offset=0, category=None):
        """
        Get the classification history.
        
        Args:
            limit: Maximum number of entries to return
            offset: Offset for pagination
            category: Filter by category if provided
            
        Returns:
            list: List of classification entries with metadata
        """
        # Build query
        query = {}
        if category:
            query["category"] = category
        
        # Execute query with pagination
        cursor = self.classifications.find(
            query,
            {"_id": 0}  # Exclude MongoDB _id from results
        ).sort("timestamp", -1).skip(offset).limit(limit)        # Convert cursor to list and ensure image_data field exists
        history = []
        for item in cursor:
            # Use our utility function to prepare image URLs
            processed_item = prepare_image_urls_for_frontend(item)
            history.append(processed_item)
        
        return history
    
    def get_stats(self, days=7):
        """
        Get classification statistics.
        
        Args:
            days: Number of days to include in daily stats
            
        Returns:
            dict: Statistics data
        """
        # Get global stats
        global_stats = self.statistics.find_one({"_id": "global"}, {"_id": 0})
        if not global_stats:
            global_stats = {
                "total_classifications": 0,
                "categories": {},
                "last_updated": None
            }
        
        # Get recent dates
        recent_dates = []
        today = datetime.now()
        for i in range(days):
            date = (today - timedelta(days=i)).strftime('%Y-%m-%d')
            recent_dates.append(date)
        
        # Get daily stats for recent days
        daily_stats = {}
        for date in sorted(recent_dates):
            stats = self.daily_stats.find_one({"_id": date}, {"_id": 0})
            if stats:
                daily_stats[date] = {
                    "total": stats.get("total", 0),
                    "categories": stats.get("categories", {})
                }
            else:
                daily_stats[date] = {"total": 0, "categories": {}}
        
        # Prepare summary
        summary = {
            "total_classifications": global_stats.get("total_classifications", 0),
            "categories": global_stats.get("categories", {}),
            "daily": daily_stats,
            "last_updated": global_stats.get("last_updated")
        }
        
        return summary
    
    def migrate_from_file_based(self, file_stats):
        """
        Migrate data from file-based stats to MongoDB.
        
        Args:
            file_stats: Instance of ClassificationStats (file-based)
            
        Returns:
            bool: True if migration was successful
        """
        try:
            # Get all data from file-based stats
            stats_data = file_stats.get_stats(days=365)  # Get all available daily data
            
            # Import global stats
            self.statistics.replace_one(
                {"_id": "global"},
                {
                    "_id": "global",
                    "total_classifications": stats_data.get("total_classifications", 0),
                    "categories": stats_data.get("categories", {}),
                    "last_updated": stats_data.get("last_updated")
                },
                upsert=True
            )
            
            # Import daily stats
            for date, daily_data in stats_data.get("daily", {}).items():
                self.daily_stats.replace_one(
                    {"_id": date},
                    {
                        "_id": date,
                        "date": date,
                        "total": daily_data.get("total", 0),
                        "categories": daily_data.get("categories", {})
                    },
                    upsert=True
                )
            
            # Import classification history
            history = file_stats.get_classification_history(limit=1000000)  # Get all history
            for item in history:
                item_id = item.get("id")
                if item_id:
                    # Check if already exists
                    if self.classifications.count_documents({"id": item_id}) == 0:
                        # Add MongoDB _id field
                        item["_id"] = item_id
                        self.classifications.insert_one(item)
            
            return True
            
        except Exception as e:
            print(f"Error migrating to MongoDB: {e}")
            import traceback
            traceback.print_exc()
            return False
