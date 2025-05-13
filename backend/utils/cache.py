import hashlib
import os
import json
import time
from datetime import datetime, timedelta

class ImageClassificationCache:
    """
    Simple cache for image classification results.
    Uses a file-based approach to store results based on image hash.
    """
    def __init__(self, cache_dir='./cache', expiry_hours=24):
        """
        Initialize the cache.
        
        Args:
            cache_dir: Directory to store cache files
            expiry_hours: Cache expiry time in hours
        """
        self.cache_dir = cache_dir
        self.expiry_hours = expiry_hours
        
        # Create cache directory if it doesn't exist
        os.makedirs(cache_dir, exist_ok=True)
        
    def _get_image_hash(self, image_data):
        """
        Generate a hash for an image to use as a cache key.
        
        Args:
            image_data: Image data as bytes
            
        Returns:
            str: SHA-256 hash of the image data
        """
        if hasattr(image_data, 'read'):
            # Handle file-like objects
            image_bytes = image_data.read()
            if hasattr(image_data, 'seek'):
                image_data.seek(0)  # Reset file pointer
        else:
            # Handle raw bytes
            image_bytes = image_data
            
        return hashlib.sha256(image_bytes).hexdigest()
    
    def _get_cache_file_path(self, image_hash):
        """Get the file path for a cache entry."""
        return os.path.join(self.cache_dir, f"{image_hash}.json")
    
    def get(self, image_data):
        """
        Get cached classification result for an image.
        
        Args:
            image_data: Image data as bytes or file-like object
            
        Returns:
            tuple: (category, confidence) if cache hit, None if cache miss
        """
        image_hash = self._get_image_hash(image_data)
        cache_file = self._get_cache_file_path(image_hash)
        
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'r') as f:
                    cache_data = json.load(f)
                
                # Check if cache is expired
                timestamp = cache_data.get('timestamp', 0)
                if time.time() - timestamp < self.expiry_hours * 3600:
                    return cache_data['category'], cache_data['confidence']
                else:
                    # Remove expired cache file
                    os.remove(cache_file)
            except (json.JSONDecodeError, KeyError, OSError):
                # If there's any error reading the cache, ignore it
                if os.path.exists(cache_file):
                    os.remove(cache_file)
        
        return None
    
    def set(self, image_data, category, confidence):
        """
        Cache classification result for an image.
        
        Args:
            image_data: Image data as bytes or file-like object
            category: The classified category
            confidence: The confidence score
            
        Returns:
            bool: True if cache was set successfully
        """
        image_hash = self._get_image_hash(image_data)
        cache_file = self._get_cache_file_path(image_hash)
        
        try:
            cache_data = {
                'category': category,
                'confidence': confidence,
                'timestamp': time.time()
            }
            
            with open(cache_file, 'w') as f:
                json.dump(cache_data, f)
            
            return True
        except OSError:
            # If there's any error writing the cache, just log and continue
            print(f"Error writing to cache file {cache_file}")
            return False
    
    def clear_expired(self):
        """
        Clear expired cache entries.
        
        Returns:
            int: Number of cache entries cleared
        """
        cleared_count = 0
        expiry_time = time.time() - (self.expiry_hours * 3600)
        
        for filename in os.listdir(self.cache_dir):
            if filename.endswith('.json'):
                cache_file = os.path.join(self.cache_dir, filename)
                try:
                    with open(cache_file, 'r') as f:
                        cache_data = json.load(f)
                    
                    timestamp = cache_data.get('timestamp', 0)
                    if timestamp < expiry_time:
                        os.remove(cache_file)
                        cleared_count += 1
                except (json.JSONDecodeError, KeyError, OSError):
                    # If there's any error, try to remove the file
                    try:
                        os.remove(cache_file)
                        cleared_count += 1
                    except OSError:
                        pass
        
        return cleared_count
