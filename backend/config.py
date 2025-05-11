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
    
    # Stats configuration
    STATS_ENABLED = os.environ.get('STATS_ENABLED', 'True') == 'True'