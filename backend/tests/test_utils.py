import unittest
import tempfile
import os
import json
import sys
import shutil
from io import BytesIO
from PIL import Image
import base64

# Add the parent directory to the path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.cache import ImageClassificationCache
from utils.stats import ClassificationStats

class TestCache(unittest.TestCase):
    """Tests for the ImageClassificationCache class."""
    
    def setUp(self):
        # Create a temporary directory for the cache
        self.temp_dir = tempfile.mkdtemp()
        self.cache = ImageClassificationCache(cache_dir=self.temp_dir, expiry_hours=1)
        
        # Create a test image
        self.test_image = self._create_test_image()
    
    def tearDown(self):
        # Remove the temporary directory
        shutil.rmtree(self.temp_dir)
    
    def _create_test_image(self):
        """Create a simple test image."""
        img = Image.new('RGB', (100, 100), color='red')
        img_io = BytesIO()
        img.save(img_io, 'JPEG')
        img_io.seek(0)
        return img_io
    
    def test_get_set(self):
        """Test setting and getting a cache entry."""
        # Set a cache entry
        self.cache.set(self.test_image, 'perro', 95.5)
        
        # Reset the file pointer
        self.test_image.seek(0)
        
        # Get the cache entry
        result = self.cache.get(self.test_image)
        
        # Check that the result is as expected
        self.assertIsNotNone(result)
        self.assertEqual(result[0], 'perro')
        self.assertEqual(result[1], 95.5)
    
    def test_get_nonexistent(self):
        """Test getting a nonexistent cache entry."""
        # Get a nonexistent cache entry
        result = self.cache.get(self.test_image)
        
        # Check that the result is None
        self.assertIsNone(result)
    
    def test_clear_expired(self):
        """Test clearing expired cache entries."""
        # Create a cache with a very short expiry time
        cache = ImageClassificationCache(cache_dir=self.temp_dir, expiry_hours=0)
        
        # Set a cache entry
        cache.set(self.test_image, 'perro', 95.5)
        
        # Clear expired cache entries
        cleared = cache.clear_expired()
        
        # Check that one entry was cleared
        self.assertEqual(cleared, 1)
        
        # Check that the entry is no longer in the cache
        self.test_image.seek(0)
        result = cache.get(self.test_image)
        self.assertIsNone(result)

class TestStats(unittest.TestCase):
    """Tests for the ClassificationStats class."""
    
    def setUp(self):
        # Create a temporary directory for the stats
        self.temp_dir = tempfile.mkdtemp()
        self.stats_file = os.path.join(self.temp_dir, 'test_stats.json')
        self.stats = ClassificationStats(stats_file=self.stats_file)
    
    def tearDown(self):
        # Remove the temporary directory
        shutil.rmtree(self.temp_dir)
    
    def test_record_classification(self):
        """Test recording a classification."""
        # Record a classification
        self.stats.record_classification('perro', 95.5)
        
        # Check that the stats file exists
        self.assertTrue(os.path.exists(self.stats_file))
        
        # Check the content of the stats file
        with open(self.stats_file, 'r') as f:
            stats_data = json.load(f)
        
        # Check that the total count is 1
        self.assertEqual(stats_data['total_classifications'], 1)
        
        # Check that the category count is 1
        self.assertEqual(stats_data['categories']['perro']['count'], 1)
        
        # Check that the confidence is correct
        self.assertEqual(stats_data['categories']['perro']['avg_confidence'], 95.5)
    
    def test_get_stats(self):
        """Test getting statistics."""
        # Record some classifications
        self.stats.record_classification('perro', 95.5)
        self.stats.record_classification('gato', 90.0)
        self.stats.record_classification('perro', 85.0)
        
        # Get the stats
        stats_data = self.stats.get_stats()
        
        # Check that the total count is 3
        self.assertEqual(stats_data['total_classifications'], 3)
        
        # Check that there are 2 categories
        self.assertEqual(len(stats_data['categories']), 2)
        
        # Check the category counts
        self.assertEqual(stats_data['categories']['perro']['count'], 2)
        self.assertEqual(stats_data['categories']['gato']['count'], 1)
        
        # Check the average confidences (with some tolerance for floating point)
        self.assertAlmostEqual(stats_data['categories']['perro']['avg_confidence'], 90.25, places=2)
        self.assertEqual(stats_data['categories']['gato']['avg_confidence'], 90.0)

if __name__ == '__main__':
    unittest.main()
