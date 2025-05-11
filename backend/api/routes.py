from flask import Blueprint, request, jsonify, current_app
from models.image_classifier import ImageClassifier
from utils.image_processing import validate_image
from utils.stats import ClassificationStats
from config import Config
import io
import os
from openai import OpenAI

api = Blueprint('api', __name__, url_prefix='/api')

# Initialize the classifier
classifier = None

# Initialize stats tracker
stats = ClassificationStats() if Config.STATS_ENABLED else None

def get_classifier():
    global classifier
    if (classifier is None):
        classifier = ImageClassifier(
            api_key=Config.OPENAI_API_KEY,
            categories=Config.IMAGE_CATEGORIES,
            use_cache=Config.USE_CACHE
        )
    return classifier

@api.route('/classify', methods=['POST'])
def classify_image():
    """
    Endpoint to classify an uploaded image.
    
    Expected request:
    - multipart/form-data with 'file' containing the image
    
    Returns:
    - JSON with 'category' and 'confidence' fields
    - Error messages with appropriate HTTP status codes
    """
    # Check if file is present in the request
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400
    
    file = request.files['file']
    
    # Check if a file was selected
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    try:
        # First, validate the image
        validate_image(file)
        
        # Get the classifier instance
        classifier = get_classifier()
          # Reset file pointer before processing
        file.seek(0)
        
        # Classify the image
        category, confidence = classifier.classify_image(file)
        
        # Record stats if enabled
        if Config.STATS_ENABLED and stats:
            # Reset file pointer before saving to history
            file.seek(0)
            stats.record_classification_with_image(
                category, 
                confidence, 
                file, 
                original_filename=file.filename
            )
        
        # Return the results
        return jsonify({
            'category': category,
            'confidence': confidence,
            'categories': Config.IMAGE_CATEGORIES  # Return all available categories
        }), 200
        
    except ValueError as e:
        # Return validation errors
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        # Log the error and return detailed error message
        error_message = str(e)
        error_type = type(e).__name__
        print(f"Error classifying image - {error_type}: {error_message}")
        
        # Prepare a more descriptive error message for the user
        if "openai" in error_message.lower():
            if "api key" in error_message.lower():
                return jsonify({
                    'error': 'Error de autenticación con la API de OpenAI. La clave API podría ser inválida.',
                    'details': error_message,
                    'type': error_type
                }), 500
            else:
                return jsonify({
                    'error': 'Error en la comunicación con la API de OpenAI.',
                    'details': error_message,
                    'type': error_type
                }), 500
        elif "timeout" in error_message.lower():
            return jsonify({
                'error': 'La solicitud a la API ha tardado demasiado tiempo. Intente nuevamente.',
                'details': error_message,
                'type': error_type
            }), 500
        elif "connection" in error_message.lower():
            return jsonify({
                'error': 'Problema de conexión a internet. Verifique su conexión e intente nuevamente.',
                'details': error_message,
                'type': error_type
            }), 500
        else:
            return jsonify({
                'error': 'Error al procesar la imagen.',
                'details': error_message,
                'type': error_type
            }), 500

@api.route('/categories', methods=['GET'])
def get_categories():
    """
    Endpoint to get all predefined categories.
    
    Returns:
    - JSON with 'categories' list
    """
    return jsonify({'categories': Config.IMAGE_CATEGORIES}), 200

@api.route('/test-openai', methods=['GET'])
def test_openai():
    """
    Endpoint to test OpenAI API connectivity.
    
    Returns:
    - JSON with 'status' field indicating if the API is working
    """
    try:
        # Initialize OpenAI client
        client = OpenAI(api_key=Config.OPENAI_API_KEY)
        
        # Make a simple API call
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Test connection"}
            ],
            max_tokens=10
        )
        
        # If we got a response, the API is working
        return jsonify({
            'status': 'OK',
            'message': 'OpenAI API is working correctly',
            'model_response': response.choices[0].message.content
        }), 200
        
    except Exception as e:
        # If there was an error, the API is not working
        return jsonify({
            'status': 'ERROR',
            'message': f'OpenAI API connection failed: {str(e)}'
        }), 500

@api.route('/stats', methods=['GET'])
def get_stats():
    """
    Endpoint to get classification statistics.
    
    Query Params:
    - days: Number of days to include in daily stats (default: 7)
    
    Returns:
    - JSON with statistics data
    """
    if not Config.STATS_ENABLED:
        return jsonify({
            'error': 'Statistics tracking is disabled in server configuration'
        }), 400
    
    try:
        # Get the number of days to include from query parameter
        days = request.args.get('days', default=7, type=int)
        days = min(max(1, days), 30)  # Limit between 1 and 30 days
        
        # Get stats data
        stats_data = stats.get_stats(days=days)
        
        return jsonify({
            'stats': stats_data
        }), 200
    
    except Exception as e:
        return jsonify({
            'error': 'Error retrieving statistics',
            'details': str(e)
        }), 500

@api.route('/history', methods=['GET'])
def get_history():
    """
    Endpoint to get classification history with images.
    
    Query Params:
    - limit: Maximum number of entries to return (default: 20, max: 50)
    - offset: Offset for pagination (default: 0)
    - category: Filter by category (optional)
    
    Returns:
    - JSON with history data including base64-encoded images
    """
    if not Config.STATS_ENABLED:
        return jsonify({
            'error': 'Statistics tracking is disabled in server configuration'
        }), 400
    
    try:
        # Get query parameters
        limit = request.args.get('limit', default=20, type=int)
        limit = min(max(1, limit), 50)  # Limit between 1 and 50 entries
        
        offset = request.args.get('offset', default=0, type=int)
        offset = max(0, offset)  # Ensure offset is not negative
        
        category = request.args.get('category', default=None, type=str)
        
        # Get history data
        history_data = stats.get_classification_history(
            limit=limit,
            offset=offset,
            category=category
        )
        
        return jsonify({
            'history': history_data,
            'total': len(history_data),
            'limit': limit,
            'offset': offset
        }), 200
    
    except Exception as e:
        return jsonify({
            'error': 'Error retrieving classification history',
            'details': str(e)
        }), 500