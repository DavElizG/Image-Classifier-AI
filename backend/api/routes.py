from flask import Blueprint, request, jsonify
from backend.models.image_classifier import classify_image
from backend.utils.image_processing import validate_image

api = Blueprint('api', __name__)

@api.route('/upload', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if not validate_image(file):
        return jsonify({'error': 'Invalid image format or size'}), 400

    category, confidence = classify_image(file)
    return jsonify({'category': category, 'confidence': confidence}), 200