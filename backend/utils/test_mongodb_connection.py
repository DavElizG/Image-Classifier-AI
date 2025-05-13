"""
Test script to verify MongoDB connection with the provided credentials.
"""
import os
import sys
from utils.db import get_mongo_client, get_database
from config import Config

def test_mongodb_connection():
    """
    Test MongoDB connection with the provided credentials.
    """
    print("Testing MongoDB connection...")
    print(f"MongoDB configuration:")
    print(f"- DB_STORAGE_TYPE: {Config.DB_STORAGE_TYPE}")
    print(f"- MONGO_DB_NAME: {Config.MONGO_DB_NAME}")
    print(f"- MONGO_URI: {Config.MONGO_URI.replace(Config.MONGO_URI.split('@')[0], 'mongodb://[CREDENTIALS_HIDDEN]') if '@' in Config.MONGO_URI else Config.MONGO_URI}")
    
    try:
        # Try to connect to MongoDB
        client = get_mongo_client()
        print("Successfully connected to MongoDB server!")
        
        # Try to access the database
        db = get_database()
        print(f"Successfully accessed database: {Config.MONGO_DB_NAME}")
          # Try to list collections
        collections = db.list_collection_names()
        print(f"Collections in database: {collections}")
        
        # Try a simple query
        print("Testing a query on 'statistics' collection...")
        stats = db.statistics.find_one({"_id": "global"})
        if stats:
            print(f"Found global statistics document:")
            print(f"- Total classifications: {stats.get('total_classifications', 0)}")
            print(f"- Categories count: {len(stats.get('categories', {}))}")
        else:
            print("No global statistics document found. This is normal for a new database.")
            
        # Check for image URLs in classifications
        if 'classifications' in collections:
            print("\nChecking classifications collection for image URLs...")
            count = db.classifications.count_documents({})
            print(f"Found {count} classification documents")
            
            if count > 0:
                # Get the most recent classification
                latest = db.classifications.find_one(
                    {}, 
                    sort=[("timestamp", -1)]
                )
                
                if latest:
                    print("\nLatest classification:")
                    print(f"  ID: {latest.get('id')}")
                    print(f"  Category: {latest.get('category')}")
                    print(f"  Timestamp: {latest.get('timestamp')}")
                    print(f"  Image URL: {latest.get('image_url')}")
                    print(f"  Image Thumbnail: {latest.get('image_thumbnail')}")
                    
                    # Verify the image URLs are accessible
                    if latest.get('image_url'):
                        print("\nVerifying image URLs are properly stored...")
                        if latest.get('image_data') == latest.get('image_url'):
                            print("✅ image_data field correctly points to image_url")
                        else:
                            print("❌ image_data field does not match image_url")
                            print(f"   image_data: {latest.get('image_data')}")
                            print(f"   image_url: {latest.get('image_url')}")
        
        print("\n✅ MongoDB connection test PASSED!")
        
    except Exception as e:
        print(f"\n❌ Error connecting to MongoDB: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    test_mongodb_connection()
