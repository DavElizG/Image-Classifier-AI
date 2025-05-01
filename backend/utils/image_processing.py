def resize_image(image, target_size=(224, 224)):
    from PIL import Image
    from io import BytesIO

    # Resize the image to the target size
    image = Image.open(BytesIO(image))
    image = image.resize(target_size, Image.ANTIALIAS)
    return image


def validate_image(file):
    import imghdr

    # Validate the image type
    valid_types = ['jpeg', 'png']
    if imghdr.what(file) not in valid_types:
        raise ValueError("Invalid image type. Only JPEG and PNG are allowed.")
    
    # Validate the file size (max 5MB)
    file.seek(0, 2)  # Move to the end of the file
    file_size = file.tell()
    file.seek(0)  # Move back to the start of the file
    if file_size > 5 * 1024 * 1024:  # 5MB
        raise ValueError("File size exceeds the maximum limit of 5MB.")
    
    return True