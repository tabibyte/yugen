from flask import Blueprint, jsonify, request, render_template
from app.services.data_service import DataService
from pathlib import Path
from werkzeug.utils import secure_filename
import os

bp = Blueprint('data', __name__, url_prefix='/')
data_service = DataService()

@bp.route('/')
def index():
    return render_template('index.html')

@bp.route('/data/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
        
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
        
    if not file.filename.endswith(('.csv', '.xlsx')):
        return jsonify({'error': 'Invalid file type'}), 400
        
    try:
        filename = secure_filename(file.filename)
        temp_path = os.path.join('instance', filename)
        file.save(temp_path)
        
        result = data_service.process_file(Path(temp_path))
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