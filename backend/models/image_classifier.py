from tensorflow import keras
from tensorflow.keras.preprocessing import image
import numpy as np

class ImageClassifier:
    def __init__(self, model_path, categories):
        self.model = keras.models.load_model(model_path)
        self.categories = categories

    def classify_image(self, img_path):
        img = image.load_img(img_path, target_size=(224, 224))  # Adjust size as needed
        img_array = image.img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0) / 255.0  # Normalize the image
        predictions = self.model.predict(img_array)
        predicted_class = np.argmax(predictions, axis=1)[0]
        confidence = predictions[0][predicted_class]
        return self.categories[predicted_class], confidence * 100  # Return category and confidence percentage

    def validate_image(self, img_path):
        valid_extensions = ['jpg', 'jpeg', 'png']
        if not any(img_path.endswith(ext) for ext in valid_extensions):
            raise ValueError("Invalid file type. Please upload a JPG or PNG image.")
        # Additional validation logic can be added here (e.g., file size)