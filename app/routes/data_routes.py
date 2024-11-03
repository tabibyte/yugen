from flask import Blueprint, jsonify, request
from app.services.data_service import DataService
from pathlib import Path

bp = Blueprint('data', __name__)
data_service = DataService()

@bp.route('/data/upload', methods=['POST'])
def upload_file():
    if 'file_path' not in request.form:
        return jsonify({'error': 'No file path provided'}), 400
    
    file_path = Path(request.form['file_path'])
    if not file_path.exists():
        return jsonify({'error': 'File not found'}), 404
        
    try:
        result = data_service.process_file(file_path)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/data/profile', methods=['GET'])
def get_profile():
    try:
        result = data_service.get_profile()
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/data/clean', methods=['POST'])
def clean_data():
    options = request.json
    try:
        result = data_service.clean_data(options)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500