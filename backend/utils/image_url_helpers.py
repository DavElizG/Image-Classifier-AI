"""
Utility functions for handling images in API responses.
"""

def prepare_image_urls_for_frontend(item):
    """
    Ensures that image URLs are properly formatted for the frontend.
    
    Args:
        item (dict): Classification record with image URLs
        
    Returns:
        dict: The record with properly formatted image URLs
    """
    # Clone the item to avoid modifying the original
    result = item.copy()
    
    # Ensure image_data points to the image URL for legacy frontend support
    if "image_url" in result and result["image_url"]:
        result["image_data"] = result["image_url"]
        
        # Ensure we have thumbnail and medium URLs
        if "image_thumbnail" not in result or not result["image_thumbnail"]:
            result["image_thumbnail"] = result["image_url"]
        if "image_medium" not in result or not result["image_medium"]:
            result["image_medium"] = result["image_url"]
    
    return result
