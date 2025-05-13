import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your_default_secret_key'
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5 MB
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
    DEBUG = os.environ.get('DEBUG', 'False') == 'True'  # Set to True for development
    HOST = os.environ.get('HOST') or '0.0.0.0'
    PORT = int(os.environ.get('PORT') or 5000)
    
    # OpenAI API Configuration
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    
    # Predefined categories for image classification
    IMAGE_CATEGORIES = [
        'perro', 'gato', 'auto', 'árbol', 'ave', 'persona', 
        'edificio', 'flor', 'paisaje', 'alimento'
    ]
      # Cache configuration
    USE_CACHE = os.environ.get('USE_CACHE', 'True') == 'True'
    CACHE_EXPIRY_HOURS = int(os.environ.get('CACHE_EXPIRY_HOURS') or 24)
    
    # ImageBB Configuration
    IMAGEBB_API_KEY = os.environ.get('IMAGEBB_API_KEY', 'bf79f82c0d0d19e2d9c15e6247dca5f7')    # Stats configuration
    STATS_ENABLED = os.environ.get('STATS_ENABLED', 'True') == 'True'
    
    # Database configuration
    # Use "file" for file-based storage or "mongodb" for MongoDB
    DB_STORAGE_TYPE = os.environ.get('DB_STORAGE_TYPE', 'mongodb')
    
    # MongoDB configuration
    # Try different MongoDB connection methods in order of preference
    # 1. Direct MONGO_URI 
    # 2. Railway MongoDB URLs
    # 3. Manual construction from credentials
    MONGO_URI = os.environ.get('MONGO_URI') or os.environ.get('MONGO_URL') or os.environ.get('MONGO_PUBLIC_URL')
    
    # Fallback to manual construction if no direct URI is provided
    if not MONGO_URI:
        mongo_host = os.environ.get('MONGOHOST', 'mongodb.railway.internal')
        mongo_port = os.environ.get('MONGOPORT', '27017')
        mongo_user = os.environ.get('MONGOUSER', 'mongo')
        mongo_password = os.environ.get('MONGOPASSWORD', 'bWgsojLFnVDtiYwGqFyQbSdqSuyqttCY')
        
        if mongo_user and mongo_password:
            MONGO_URI = f"mongodb://{mongo_user}:{mongo_password}@{mongo_host}:{mongo_port}"
        else:
            MONGO_URI = f"mongodb://{mongo_host}:{mongo_port}"
    
    MONGO_DB_NAME = os.environ.get('MONGO_DB_NAME', 'image_classifier_db')