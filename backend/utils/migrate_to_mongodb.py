"""
Tool to migrate classification data from file-based storage to MongoDB.
"""
import os
import sys
import time
from config import Config
from utils.stats_new import ClassificationStats
from utils.mongodb_stats import MongoDBStats
from utils.db import init_db, close_mongo_connection

def migrate_to_mongodb():
    """
    Migrate classification data from file-based storage to MongoDB.
    """
    print("Starting migration from file-based storage to MongoDB...")
    
    try:
        # Initialize MongoDB
        init_db()
        
        # Create file-based stats instance
        file_stats = ClassificationStats()
        
        # Create MongoDB stats instance
        mongo_stats = MongoDBStats()
        
        # Start migration
        print("Migrating classification statistics and history...")
        
        # Migrate data
        success = mongo_stats.migrate_from_file_based(file_stats)
        
        if success:
            print("Migration completed successfully!")
            print("\nTo start using MongoDB, update your environment variables:")
            print("- Set DB_STORAGE_TYPE=mongodb")
            print("- Optionally set MONGO_URI and MONGO_DB_NAME if not using defaults")
            
            print("\nYou can add these to your .env file or set them as environment variables.")
            
            # Suggest backup
            print("\nIt's recommended to keep your file-based data as backup.")
            print("You can rename the stats directory to stats_backup if you want.")
        else:
            print("Migration failed. Please check the logs for errors.")
    
    except Exception as e:
        print(f"Error during migration: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Close MongoDB connection
        close_mongo_connection()

if __name__ == "__main__":
    # Check if MongoDB is configured
    if Config.DB_STORAGE_TYPE != 'mongodb':
        print("Warning: Your DB_STORAGE_TYPE is not set to 'mongodb'.")
        print("The migration will still proceed, but you'll need to update this setting to use MongoDB.")
        print("Press Enter to continue or Ctrl+C to cancel...")
        input()
    
    migrate_to_mongodb()
