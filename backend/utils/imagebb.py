import requests
import base64
import os
import time
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# API key predeterminada
DEFAULT_API_KEY = 'bf79f82c0d0d19e2d9c15e6247dca5f7'

def upload_image_to_imagebb(image_data, api_key=None, name=None):
    """
    Sube una imagen a ImageBB.
    
    Args:
        image_data: Bytes de la imagen o objeto tipo archivo
        api_key: API key de ImageBB (opcional)
        name: Nombre para la imagen (opcional)
        
    Returns:
        dict: Datos de la imagen subida o None si falla
    """
    try:
        # Usar la API key proporcionada o la predeterminada
        api_key = api_key or os.environ.get('IMAGEBB_API_KEY', DEFAULT_API_KEY)
        upload_url = "https://api.imgbb.com/1/upload"
        
        # Si image_data es un objeto tipo archivo, obtener los bytes
        if hasattr(image_data, 'read'):
            img_bytes = image_data.read()
            if hasattr(image_data, 'seek'):
                image_data.seek(0)  # Reset file pointer
        else:
            img_bytes = image_data
            
        # Codificar imagen en base64
        base64_image = base64.b64encode(img_bytes).decode('utf-8')
        
        # Preparar payload para la petición
        payload = {
            'key': api_key,
            'image': base64_image,
        }
        
        if name:
            payload['name'] = name
            
        # Realizar la petición a la API de ImageBB
        response = requests.post(upload_url, data=payload)
        response.raise_for_status()  # Lanzar excepción si hay error HTTP
        
        result = response.json()
        
        # Verificar si la subida fue exitosa
        if result.get('success'):
            return result.get('data')
        else:
            print(f"Error subiendo imagen a ImageBB: {result.get('error', {}).get('message', 'Unknown error')}")
            return None
            
    except Exception as e:
        print(f"Error subiendo imagen a ImageBB: {str(e)}")
        return None

class ImageBBUploader:
    def __init__(self, api_key=None):
        """
        Inicializa el uploader de ImageBB.
        
        Args:
            api_key: API key de ImageBB. Si no se proporciona, se intentará leer de las variables de entorno.
        """
        self.api_key = api_key or os.environ.get('IMAGEBB_API_KEY', DEFAULT_API_KEY)
        self.upload_url = "https://api.imgbb.com/1/upload"
        
    def upload_image(self, image_data, name=None):
        """
        Sube una imagen a ImageBB.
        
        Args:
            image_data: Bytes de la imagen o objeto tipo archivo
            name: Nombre para la imagen (opcional)
            
        Returns:
            dict: Datos de la imagen subida o None si falla
        """
        return upload_image_to_imagebb(image_data, self.api_key, name)
            
    def upload_with_retry(self, image_data, name=None, max_retries=3, delay=2):
        """
        Intenta subir una imagen con reintentos en caso de fallo.
        
        Args:
            image_data: Bytes de la imagen o objeto tipo archivo
            name: Nombre para la imagen (opcional)
            max_retries: Número máximo de intentos
            delay: Tiempo de espera entre intentos (segundos)
            
        Returns:
            dict: Datos de la imagen subida o None si fallan todos los intentos
        """
        for attempt in range(max_retries):
            result = self.upload_image(image_data, name)
            if result:
                return result
                
            # Si hay error pero quedan intentos, esperar y reintentar
            if attempt < max_retries - 1:
                print(f"Reintentando subida de imagen ({attempt+1}/{max_retries})...")
                time.sleep(delay)
                
        return None