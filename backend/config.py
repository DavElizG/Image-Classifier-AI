import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your_default_secret_key'
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5 MB
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    MODEL_PATH = os.environ.get('MODEL_PATH') or 'path/to/your/model'  # Update with your model path
    DEBUG = os.environ.get('DEBUG', 'False') == 'True'  # Set to True for development
    HOST = os.environ.get('HOST') or '0.0.0.0'
    PORT = os.environ.get('PORT') or 5000