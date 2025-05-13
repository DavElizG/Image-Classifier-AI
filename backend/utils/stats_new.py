import os
import json
import base64
import time
import hashlib
import requests
from datetime import datetime, timedelta
from collections import defaultdict
from config import Config
from utils.imagebb import upload_image_to_imagebb
from utils.image_url_helpers import prepare_image_urls_for_frontend

class ClassificationStats:
    """
    Tracks statistics for image classifications.
    """
    
    def __init__(self, stats_file='./stats/classification_stats.json', history_dir='./stats/history'):
        """
        Initialize the statistics tracker.
        
        Args:
            stats_file: File path to store statistics
            history_dir: Directory to store classification history with images
        """
        # Convert relative paths to absolute paths if they are relative
        if not os.path.isabs(stats_file):
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            stats_file = os.path.join(base_dir, stats_file)
        
        if not os.path.isabs(history_dir):
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            history_dir = os.path.join(base_dir, history_dir)
            
        self.stats_file = stats_file
        self.stats_dir = os.path.dirname(stats_file)
        self.history_dir = history_dir
        
        print(f"Stats file: {self.stats_file}")
        print(f"History directory: {self.history_dir}")
        
        # Create stats directories if they don't exist
        os.makedirs(self.stats_dir, exist_ok=True)
        os.makedirs(self.history_dir, exist_ok=True)
        
        # Initialize or load stats
        self.stats = self._load_stats()
    
    def _load_stats(self):
        """Load statistics from file or create new if not exists."""
        if os.path.exists(self.stats_file):
            try:
                with open(self.stats_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, OSError):
                # If there's any error reading the file, create new stats
                pass
        
        # Initialize new stats structure
        return {
            'total_classifications': 0,
            'categories': {},
            'daily': {},
            'last_updated': datetime.now().isoformat()
        }
    
    def _save_stats(self):
        """Save statistics to file."""
        try:
            with open(self.stats_file, 'w') as f:
                json.dump(self.stats, f, indent=2)
        except OSError:
            print(f"Error writing to stats file {self.stats_file}")
    
    def record_classification(self, category, confidence):
        """
        Record a new classification.
        
        Args:
            category: The classified category
            confidence: The confidence score
        """
        # Update total count
        self.stats['total_classifications'] += 1
        
        # Update category stats
        if category not in self.stats['categories']:
            self.stats['categories'][category] = {
                'count': 0,
                'avg_confidence': 0
            }
        
        cat_stats = self.stats['categories'][category]
        # Update average confidence (weighted)
        cat_stats['avg_confidence'] = (
            (cat_stats['avg_confidence'] * cat_stats['count'] + confidence) / 
            (cat_stats['count'] + 1)
        )
        cat_stats['count'] += 1
        
        # Update daily stats
        today = datetime.now().strftime('%Y-%m-%d')
        if today not in self.stats['daily']:
            self.stats['daily'][today] = {
                'total': 0,
                'categories': {}
            }
        
        daily = self.stats['daily'][today]
        daily['total'] += 1
        
        if category not in daily['categories']:
            daily['categories'][category] = 0
        daily['categories'][category] += 1
        
        # Update last updated timestamp
        self.stats['last_updated'] = datetime.now().isoformat()
        
        # Save to file
        self._save_stats()
    
    def get_stats(self, days=7):
        """
        Get classification statistics.
        
        Args:
            days: Number of days to include in daily stats
            
        Returns:
            dict: Statistics data
        """
        # Clean up old daily data
        self._cleanup_old_daily_data(days)
        
        # Get recent daily stats
        recent_dates = self._get_recent_dates(days)
        daily_stats = {}
        
        for date in recent_dates:
            if date in self.stats['daily']:
                daily_stats[date] = self.stats['daily'][date]
            else:
                daily_stats[date] = {'total': 0, 'categories': {}}
        
        # Prepare summary
        summary = {
            'total_classifications': self.stats['total_classifications'],
            'categories': self.stats['categories'],
            'daily': daily_stats,
            'last_updated': self.stats['last_updated']
        }
        
        return summary
    
    def _cleanup_old_daily_data(self, keep_days=30):
        """
        Remove daily data older than keep_days.
        
        Args:
            keep_days: Number of days to keep
        """
        if 'daily' not in self.stats:
            return
        
        cutoff_date = (datetime.now() - timedelta(days=keep_days)).strftime('%Y-%m-%d')
        new_daily = {}
        
        for date, data in self.stats['daily'].items():
            if date >= cutoff_date:
                new_daily[date] = data
        
        self.stats['daily'] = new_daily
        self._save_stats()
    
    def _get_recent_dates(self, days=7):
        """
        Get a list of recent dates in YYYY-MM-DD format.
        
        Args:
            days: Number of days to include
            
        Returns:
            list: List of date strings
        """
        today = datetime.now()
        dates = []
        
        for i in range(days):
            date = (today - timedelta(days=i)).strftime('%Y-%m-%d')
            dates.append(date)
        
        return sorted(dates)
    
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
        
        # Create a unique identifier using timestamp and a random component
        unique_id = f"{timestamp}-{hashlib.md5(str(time.time()).encode()).hexdigest()[:8]}"
        
        # Record basic classification data
        self.record_classification(category, confidence)
        
        # Save image data for history
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
                'id': unique_id,
                'timestamp': timestamp,
                'category': category,
                'confidence': confidence,
                'original_filename': original_filename or 'unknown.jpg',
                'image_url': upload_result.get('url'),
                'image_thumbnail': upload_result.get('thumb', {}).get('url'),
                'image_medium': upload_result.get('medium', {}).get('url'),
                'delete_url': upload_result.get('delete_url')
            }
            
            # Save the metadata
            metadata_path = os.path.join(self.history_dir, f"{unique_id}.json")
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
                
            print(f"Image uploaded to ImageBB: {upload_result.get('url')}")
            return unique_id
            
        except Exception as e:
            print(f"Error saving image for history: {e}")
            # Print more detailed error information
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
        history = []
        
        try:
            # Get all JSON metadata files in history directory
            metadata_files = [f for f in os.listdir(self.history_dir) if f.endswith('.json')]
            
            # Sort by modification time (newest first)
            metadata_files.sort(key=lambda f: os.path.getmtime(os.path.join(self.history_dir, f)), reverse=True)
            
            # Apply pagination
            metadata_files = metadata_files[offset:offset+limit]
            
            for metadata_file in metadata_files:
                try:
                    # Load metadata
                    with open(os.path.join(self.history_dir, metadata_file), 'r') as f:
                        metadata = json.load(f)
                    
                    # Skip if category filter is applied and doesn't match
                    if category and metadata.get('category', '').lower() != category.lower():
                        continue
                    
                    # For older entries that might not have ImageBB URLs
                    if 'image_url' not in metadata:
                        # Check if the corresponding image exists
                        image_id = metadata.get('id')
                        image_path = os.path.join(self.history_dir, f"{image_id}.jpg")
                        if os.path.exists(image_path):
                            # Read image as base64 for sending to frontend
                            with open(image_path, 'rb') as img_file:
                                img_data = img_file.read()
                                img_base64 = base64.b64encode(img_data).decode('utf-8')
                            
                            # Add image data to metadata
                            metadata['image_data'] = f"data:image/jpeg;base64,{img_base64}"
                    else:
                        # Use the ImageBB URLs directly
                        metadata['image_data'] = metadata['image_url']
                    
                    # Process the metadata to ensure all image URLs are properly set
                    processed_metadata = prepare_image_urls_for_frontend(metadata)
                    
                    # Add to history list
                    history.append(processed_metadata)
                except Exception as e:
                    print(f"Error processing history file {metadata_file}: {e}")
                    continue
        except Exception as e:
            print(f"Error retrieving classification history: {e}")
        
        return history
