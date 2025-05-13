import os
import base64
from openai import OpenAI
import tempfile
from io import BytesIO
from PIL import Image
from utils.cache import ImageClassificationCache
from utils.image_processing import optimize_image

class ImageClassifier:
    def __init__(self, api_key, categories, use_cache=True):
        self.client = OpenAI(api_key=api_key)
        self.categories = categories
        self.use_cache = use_cache
        self.cache = ImageClassificationCache() if use_cache else None

    def _format_prompt(self):
        """Format the prompt for the OpenAI API with the available categories."""
        categories_str = ", ".join(self.categories)
        return f"Classify this image into one of the following categories: {categories_str}. Return only the category name and a confidence percentage (0-100)."
        
    def classify_image(self, image_data):
        """
        Classify an image using OpenAI's Vision API.
        
        Args:
            image_data: The image data as bytes or a file-like object
            
        Returns:
            tuple: (category, confidence_percentage)
        """
        # Check cache first if enabled
        if self.use_cache:
            cached_result = self.cache.get(image_data)
            if cached_result:
                print("Using cached result for image classification")
                return cached_result
        
        temp_file_path = None
        try:
            # If image_data is a file-like object from Flask, read the content
            if hasattr(image_data, 'read'):
                image_bytes = image_data.read()
                if hasattr(image_data, 'seek'):
                    image_data.seek(0)  # Reset file pointer for potential future operations
            else:
                # Assume image_data is already bytes
                image_bytes = image_data
            
            # Optimize the image before processing
            optimized_image = optimize_image(image_bytes)
            
            # Convert the optimized image to a temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp_file:
                temp_file.write(optimized_image.getvalue())
                temp_file_path = temp_file.name
            
            # Encode the image as base64
            with open(temp_file_path, "rb") as image_file:
                base64_image = base64.b64encode(image_file.read()).decode('utf-8')
            
            # Create the prompt for classification
            prompt = self._format_prompt()
            
            # Call the OpenAI API - Using gpt-4o instead of gpt-4-vision-preview
            try:
                response = self.client.chat.completions.create(
                    model="gpt-4o",  # Using GPT-4o which supports vision
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": prompt},
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:image/jpeg;base64,{base64_image}"
                                    }
                                }
                            ]
                        }
                    ],
                    max_tokens=100
                )
            except Exception as api_error:
                # Detailed API error handling
                error_message = str(api_error)
                if "API key" in error_message:
                    raise Exception(f"Error de autenticación con la API de OpenAI: {error_message}")
                elif "model" in error_message and ("unavailable" in error_message or "not found" in error_message):
                    raise Exception(f"El modelo de OpenAI no está disponible o no existe: {error_message}")
                elif "rate limit" in error_message.lower():
                    raise Exception(f"Se ha excedido el límite de peticiones a la API de OpenAI: {error_message}")
                elif "timeout" in error_message.lower():
                    raise Exception(f"La petición a la API de OpenAI ha expirado: {error_message}")
                else:
                    raise Exception(f"Error al comunicarse con la API de OpenAI: {error_message}")
            
            # Parse the response
            response_text = response.choices[0].message.content.strip()
            
            # Extract category and confidence from response
            # The response format should be: "Category: 95%"
            for category in self.categories:
                if category.lower() in response_text.lower():
                    # Find a number that represents confidence
                    import re
                    confidence_match = re.search(r'(\d+(?:\.\d+)?)%?', response_text)
                    if confidence_match:
                        confidence = float(confidence_match.group(1))
                        
                        # Store result in cache if enabled
                        if self.use_cache:
                            # Reset file pointer if it's a file-like object
                            if hasattr(image_data, 'seek'):
                                image_data.seek(0)
                            self.cache.set(image_data, category, confidence)
                        
                        return category, confidence
                    else:
                        # If no confidence percentage is found, default to a high value
                        if self.use_cache:
                            # Reset file pointer if it's a file-like object
                            if hasattr(image_data, 'seek'):
                                image_data.seek(0)
                            self.cache.set(image_data, category, 90.0)
                        return category, 90.0
            
            # If no matching category was found
            return "Unknown", 0.0
            
        except Exception as e:
            print(f"Error detallado en classify_image: {type(e).__name__} - {str(e)}")
            raise
        finally:
            # Always clean up the temporary file
            if temp_file_path and os.path.exists(temp_file_path):
                try:
                    os.unlink(temp_file_path)
                except Exception as cleanup_error:
                    print(f"Error al eliminar archivo temporal: {str(cleanup_error)}")

    def validate_image(self, image_data):
        """
        Validate an image file.
        
        Args:
            image_data: The image data as bytes or a file-like object
            
        Returns:
            bool: True if the image is valid, otherwise raises ValueError
        """
        try:
            # If image_data is a file-like object from Flask, read the content
            if hasattr(image_data, 'read'):
                image_bytes = image_data.read()
                if hasattr(image_data, 'seek'):
                    image_data.seek(0)  # Reset file pointer
            else:
                # Assume image_data is already bytes
                image_bytes = image_data
            
            # Try to open the image with Pillow to validate it
            img = Image.open(BytesIO(image_bytes))
            img.verify()  # Verify that it's a valid image
            
            # Check file size (max 5MB)
            if len(image_bytes) > 5 * 1024 * 1024:
                raise ValueError("El tamaño de la imagen excede el límite de 5MB")
            
            return True
        except Exception as e:
            raise ValueError(f"Imagen inválida: {str(e)}")