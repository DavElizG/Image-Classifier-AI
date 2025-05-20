"""
MongoDB database utilities for the Image Classifier API.
"""
import os
from pymongo import MongoClient
from config import Config

# MongoDB connection singleton
_client = None

def get_mongo_client():
    """
    Get MongoDB client instance (singleton pattern).
    
    Returns:
        MongoClient: MongoDB client instance
    """
    global _client
    if _client is None:        # Try to use the provided Railway MongoDB connection info if available
        mongo_public_url = os.environ.get('MONGO_PUBLIC_URL')
        mongo_url = os.environ.get('MONGO_URL')
        
        # Cuando se ejecuta localmente, siempre usar la URL pública
        if os.environ.get('RAILWAY_ENVIRONMENT') != 'production' and mongo_public_url:
            print('Usando MongoDB URL pública para entorno local')
            mongo_uri = mongo_public_url
        # En Railway, usar la URL interna para mejor rendimiento
        elif mongo_url and os.environ.get('RAILWAY_ENVIRONMENT') == 'production':
            mongo_uri = mongo_url
        elif mongo_public_url:
            mongo_uri = mongo_public_url
        else:
            # Fallback to the config or manually construct from env variables
            mongo_uri = Config.MONGO_URI or os.environ.get('MONGO_URI')
            
            # If no URI is configured, try to build one from individual credentials
            if not mongo_uri:
                mongo_host = os.environ.get('MONGOHOST', 'localhost')
                mongo_port = os.environ.get('MONGOPORT', '27017')
                mongo_user = os.environ.get('MONGOUSER')
                mongo_password = os.environ.get('MONGOPASSWORD')
                
                if mongo_user and mongo_password:
                    mongo_uri = f"mongodb://{mongo_user}:{mongo_password}@{mongo_host}:{mongo_port}"
                else:
                    mongo_uri = f"mongodb://{mongo_host}:{mongo_port}"
        
        print(f"Connecting to MongoDB using: {mongo_uri.replace(mongo_uri.split('@')[0], 'mongodb://[CREDENTIALS_HIDDEN]') if '@' in mongo_uri else mongo_uri}")
        _client = MongoClient(mongo_uri)
    return _client

def get_database():
    """
    Get the database instance.
    
    Returns:
        Database: MongoDB database instance
    """
    client = get_mongo_client()
    db_name = Config.MONGO_DB_NAME or os.environ.get('MONGO_DB_NAME', 'image_classifier_db')
    return client[db_name]

def close_mongo_connection():
    """Close MongoDB connection."""
    global _client
    if _client:
        _client.close()
        _client = None

def init_db():
    """
    Initialize database with required collections and indexes.
    """
    db = get_database()
    
    # Create indexes if they don't exist
    if 'classifications' not in db.list_collection_names():
        db.create_collection('classifications')
        db.classifications.create_index([("timestamp", -1)])
        db.classifications.create_index([("category", 1)])
    
    if 'daily_stats' not in db.list_collection_names():
        db.create_collection('daily_stats')
        db.daily_stats.create_index([("date", -1)])
    
    if 'statistics' not in db.list_collection_names():
        db.create_collection('statistics')
        # Insert initial global stats document if it doesn't exist
        if db.statistics.count_documents({"_id": "global"}) == 0:
            db.statistics.insert_one({
                "_id": "global",
                "total_classifications": 0,
                "last_updated": None,
                "categories": {}
            })
    
    print("Database initialized successfully")
