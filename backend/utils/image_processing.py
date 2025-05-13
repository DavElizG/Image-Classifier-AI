from PIL import Image, ImageOps
from io import BytesIO

def resize_image(image_data, target_size=(224, 224)):
    """
    Resize an image to the target size.
    
    Args:
        image_data: The image data as bytes or a file-like object
        target_size: The target dimensions as (width, height)
        
    Returns:
        PIL.Image: The resized image
    """
    # Handle file-like objects
    if hasattr(image_data, 'read'):
        image_bytes = image_data.read()
        if hasattr(image_data, 'seek'):
            image_data.seek(0)  # Reset file pointer
    else:
        image_bytes = image_data
    
    # Open and resize the image
    image = Image.open(BytesIO(image_bytes))
    image = image.resize(target_size, Image.LANCZOS)  # LANCZOS is the replacement for ANTIALIAS
    return image

def optimize_image(image_data, max_size=(1024, 1024), quality=85):
    """
    Optimizes an image for processing.
    
    Args:
        image_data: The image data as bytes or a file-like object
        max_size: Maximum size (width, height) to resize to
        quality: JPEG compression quality (1-100)
        
    Returns:
        BytesIO: File-like object with the optimized image
    """
    try:
        # Handle file-like objects
        if hasattr(image_data, 'read'):
            image_bytes = image_data.read()
            if hasattr(image_data, 'seek'):
                image_data.seek(0)  # Reset file pointer
        else:
            image_bytes = image_data
        
        # Open the image
        img = Image.open(BytesIO(image_bytes))
        
        # Convert to RGB if needed (e.g., if RGBA or indexed modes)
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Resize if necessary
        if img.width > max_size[0] or img.height > max_size[1]:
            img.thumbnail(max_size, Image.LANCZOS)
        
        # Apply basic image enhancements
        img = ImageOps.autocontrast(img, cutoff=0.5)
        
        # Save the optimized image to a buffer
        output = BytesIO()
        img.save(output, format='JPEG', quality=quality, optimize=True)
        output.seek(0)
        
        return output
    except Exception as e:
        raise ValueError(f"Error optimizing image: {str(e)}")


def validate_image(file):
    """
    Validate an image file.
    
    Args:
        file: A file-like object from Flask's request.files
        
    Returns:
        bool: True if valid, otherwise raises ValueError
    """
    import imghdr
    from flask import current_app
    
    # Check if the file is actually an image
    file_contents = file.read()
    file.seek(0)  # Reset file pointer
    
    image_type = imghdr.what(None, h=file_contents)
    if not image_type or image_type not in ['jpeg', 'png']:
        raise ValueError("Invalid image type. Only JPEG and PNG are allowed.")
    
    # Validate the file size (max 5MB)
    file_size = len(file_contents)
    if file_size > 5 * 1024 * 1024:  # 5MB
        raise ValueError("File size exceeds the maximum limit of 5MB.")
    
    # Try to open the image with PIL to ensure it's a valid image
    try:
        Image.open(BytesIO(file_contents))
    except Exception:
        raise ValueError("The file is not a valid image.")
    
    return True


def get_image_format(filename):
    """
    Get the format of an image from its filename.
    
    Args:
        filename: The filename of the image
        
    Returns:
        str: The format of the image ('JPEG', 'PNG', etc.)
    """
    extension = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
    
    if extension in ['jpg', 'jpeg']:
        return 'JPEG'
    elif extension == 'png':
        return 'PNG'
    else:
        return None