from flask import Blueprint, jsonify, request, render_template, session
from app.services.data_service import DataService
from pathlib import Path
from werkzeug.utils import secure_filename
import os
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score, mean_squared_error
import numpy as np
import pandas as pd
from app.services.model_service import ModelService

bp = Blueprint('data', __name__, url_prefix='/')
data_service = DataService()
model_service = ModelService()

@bp.route('/')
def index():
    return render_template('index.html')

@bp.route('/data/upload', methods=['POST'])
def upload_file():
    """Stores the data temporarily in the session and returns the data info"""
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
        
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
        
    if not file.filename.endswith(('.csv', '.xlsx')):
        return jsonify({'error': 'Invalid file type'}), 400

    try:
        
        # Save file to instance folder
        
        filename = secure_filename(file.filename)
        os.makedirs('instance', exist_ok=True)
        file_path = Path(os.path.join('instance', filename)).absolute()
        file.save(file_path)
        
        result = data_service.process_file(file_path)
        
        session['file_path'] = str(file_path.absolute())

        print(f"File path stored in session: {session['file_path']}")
        
        return jsonify(result)
    
    except Exception as e:
        print("Upload error:", str(e))
        return jsonify({'error': str(e)}), 500

@bp.route('/data/profile', methods=['GET'])
def get_profile():
    try:
        result = data_service.get_profile()
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@bp.route('/data/visualize', methods=['POST'])
def create_visualization():
    try:
        plot_type = request.json.get('type')
        x = request.json.get('x')
        y = request.json.get('y')
        
        result = data_service.get_plot_data(plot_type, x, y)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@bp.route('/data/clean', methods=['POST'])
def clean_data():
    print("Clean data called, session state:", dict(session))  # Debug log
    options = request.json
    try:
        result = data_service.clean_data(options)
        # Update session with cleaned data
        if 'data' in result:
            print("Updating session with cleaned data")  # Debug log
            session['df'] = result['data'].to_json()
            print("Session after cleaning:", dict(session))  # Debug log
        return jsonify(result)
    except Exception as e:
        print("Clean error:", str(e))  # Debug log
        return jsonify({'error': str(e)}), 500

@bp.route('/modeling', methods=['GET', 'POST'])
def modeling():
    try:
        if 'file_path' not in session:
            print("No file path in session")  # Debug log
            return jsonify({'error': 'No data available'}), 400
            
        file_path = Path(session['file_path'])
        model_service.load_data(file_path)
        
        print(f"Checking file path: {file_path}")  # Debug log
        
        if not file_path.exists():
            print(f"File not found: {file_path}")  # Debug log
            return jsonify({'error': f'File not found: {file_path}'}), 400
        
        if request.method == 'POST':
            data = request.get_json()
            results = model_service.train_linear_regression(
                data['feature_columns'],
                data['target_column'],
                float(data['test_size'])
            )
            return jsonify(results)
        
        df = pd.read_json(session['df'])
        numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()
        return jsonify({
            'numeric_columns': numeric_columns,
            'success': True
        })
        
    except Exception as e:
        print("Modeling error:", str(e))
        return jsonify({'error': str(e)}), 500