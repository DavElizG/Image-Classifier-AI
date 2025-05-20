from flask import Flask, jsonify, send_from_directory, request
from api.routes import api
from config import Config
from flask_swagger_ui import get_swaggerui_blueprint
from flask_cors import CORS
import os
import atexit

def create_app():
    app = Flask(__name__)
      # Configuración de CORS más permisiva para resolver problemas de CORS
    app.config['CORS_HEADERS'] = 'Content-Type'
    CORS(app, resources={r"/*": {
        "origins": ["http://localhost:5173", "http://127.0.0.1:5173", "*"], 
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization", "X-Requested-With", "Accept", "Origin", "Access-Control-Request-Method", "Access-Control-Request-Headers"],
        "supports_credentials": True,
        "expose_headers": ["Content-Type", "X-CSRFToken", "Authorization"],
        "max_age": 3600
    }})
    
    # Load configuration from Config class
    app.config.from_object(Config)
    
    # Initialize database if using MongoDB
    if Config.DB_STORAGE_TYPE == 'mongodb':
        from utils.db import init_db, close_mongo_connection
        init_db()
        # Register function to close MongoDB connection on application shutdown
        atexit.register(close_mongo_connection)
    
    # Register the API blueprint
    app.register_blueprint(api)
    
    # Configure maximum content length
    app.config['MAX_CONTENT_LENGTH'] = Config.MAX_CONTENT_LENGTH
    
    # Create necessary directories
    os.makedirs(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static'), exist_ok=True)
    os.makedirs(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cache'), exist_ok=True)
    os.makedirs(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'stats'), exist_ok=True)
    
    # Configure Swagger
    SWAGGER_URL = '/api/docs'  # URL for exposing Swagger UI
    API_URL = '/static/swagger.json'  # Our API url (can also be a remote url)
    
    # Register Swagger UI blueprint
    swaggerui_blueprint = get_swaggerui_blueprint(
        SWAGGER_URL,
        API_URL,
        config={
            'app_name': "API de Clasificador de Imágenes"
        }
    )
    app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)
    
    # Serve swagger.json
    @app.route('/static/<path:path>')
    def send_static(path):
        return send_from_directory('static', path)
    
    @app.route('/')
    def home():
        return jsonify({
            "message": "Bienvenido a la API de Clasificación de Imágenes", 
            "version": "1.0",
            "endpoints": {
                "/api/classify": "POST - Clasifica una imagen en una de las categorías predefinidas",
                "/api/categories": "GET - Obtiene la lista de categorías disponibles",
                "/api/stats": "GET - Obtiene estadísticas de clasificación",
                "/api/history": "GET - Obtiene el historial de clasificaciones",
                "/api/test-openai": "GET - Prueba la conexión con la API de OpenAI",
                "/api/docs": "GET - Documentación de la API (Swagger UI)"
            }
        })
    
    @app.errorhandler(413)
    def request_entity_too_large(error):
        return jsonify({
            'error': 'El archivo excede el tamaño máximo permitido (5MB)'
        }), 413
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'error': 'Endpoint no encontrado'
        }), 404
    
    @app.errorhandler(500)
    def internal_server_error(error):
        return jsonify({
            'error': 'Error interno del servidor'
        }), 500
      # Manejador global para asegurarnos que todos los endpoints respetan CORS
    @app.after_request
    def add_cors_headers(response):
        origin = request.headers.get('Origin')
        # Si la solicitud viene de localhost:5173, permite ese origen específicamente
        if origin and ('http://localhost:5173' in origin or 'http://127.0.0.1:5173' in origin):
            response.headers.add('Access-Control-Allow-Origin', origin)
        else:
            response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,X-Requested-With,Accept,Origin')
        response.headers.add('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE,OPTIONS')
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        return response
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(
        host=Config.HOST, 
        port=Config.PORT, 
        debug=Config.DEBUG
    )
