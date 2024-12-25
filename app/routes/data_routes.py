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
        
        # Store DataFrame in session
        if 'data' in result:
            print("Storing DataFrame in session")  # Debug log
            session['df'] = result['data'].to_json()
            print("Session after upload:", dict(session))  # Debug log
            
        return jsonify(result)
    except Exception as e:
        print("Upload error:", str(e))  # Debug log
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
    print("Modeling route called")  # Debug log
    print("Session state:", dict(session))  # Debug log
    try:
        if 'df' not in session:
            print("No DataFrame in session")  # Debug log
            return jsonify({'error': 'No data available'}), 400
            
        df = pd.read_json(session['df'])
        numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()
        print(f"Found {len(numeric_columns)} numeric columns")  # Debug log
        
        if request.method == 'POST':
            data = request.get_json()
            print("Received model request:", data)  # Debug log
            
            if not data:
                return jsonify({'error': 'No data provided'}), 400

            # Validate inputs
            if not all(k in data for k in ['test_size', 'target_column', 'feature_columns']):
                missing = [k for k in ['test_size', 'target_column', 'feature_columns'] if k not in data]
                return jsonify({'error': f'Missing parameters: {", ".join(missing)}'}), 400
                
            # Validate test_size
            try:
                test_size = float(data['test_size'])
                if not 0 < test_size < 1:
                    return jsonify({'error': 'Test size must be between 0 and 1'}), 400
            except ValueError:
                return jsonify({'error': 'Invalid test size value'}), 400
                
            # Validate columns
            if data['target_column'] not in numeric_columns:
                return jsonify({'error': 'Invalid target column'}), 400
                
            invalid_features = [col for col in data['feature_columns'] if col not in numeric_columns]
            if invalid_features:
                return jsonify({'error': f'Invalid feature columns: {", ".join(invalid_features)}'}), 400

            results = model_service.train_linear_regression(
                df,
                data['feature_columns'],
                data['target_column'],
                test_size
            )
            
            print("Model results:", results)  # Debug log
            return jsonify({'success': True, 'results': results})
            
        return jsonify({
            'success': True,
            'numeric_columns': numeric_columns
        })

    except Exception as e:
        print("Error in modeling:", str(e))
        return jsonify({'error': str(e)}), 500