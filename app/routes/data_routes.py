from flask import Blueprint, jsonify, request, render_template, session
import numpy as np
import pandas as pd
from pathlib import Path
from werkzeug.utils import secure_filename
import os
from app.services.data_service import DataService
from app.services.model_service import ModelService

bp = Blueprint('data', __name__, url_prefix='/')
data_service = DataService()
model_service = ModelService()

@bp.route('/')
def index():
    return render_template('index.html')

@bp.route('/data/upload', methods=['POST'])
def upload_file():
    """
    Handle file upload via POST request.
    This route accepts a file upload, validates the file type, saves the file to the instance folder,
    processes the file using the data_service, and stores the file path in the session.
    Returns:
        Response: JSON response containing basic info about the data or an error message.
    Raises:
        Exception: If there is an error during file upload or processing.
    HTTP Status Codes:
        200: File uploaded and processed successfully.
        400: Bad request due to missing file, no selected file, or invalid file type.
        500: Internal server error during file upload or processing.
        
    """
    
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
    """
    Route to get user profile data.
    This route handles GET requests to retrieve user profile data from the data service.
    Returns:
        Response: A JSON response containing profiling data or an error message.
    Raises:
        Exception: If an error occurs while retrieving the profile data, a JSON response with the error message and a 500 status code is returned.
    """
    
    try:
        result = data_service.get_profile()
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@bp.route('/data/visualize', methods=['POST'])
def create_visualization():
    """
    Route to create a data visualization.
    This route handles POST requests to generate a plot based on the provided plot type and data columns.
    Returns:
        Response: A JSON response containing the data for plotting or an error message.
    Raises:
        Exception: If an error occurs while generating the plot, a JSON response with the error message and a 500 status code is returned.
    """
    
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
    """
    Route to clean data.
    This route handles POST requests to clean the data based on provided options.
    Args:
        None
    Returns:
        Response: A JSON response containing the cleaned data or an error message.
    Raises:
        Exception: If an error occurs while cleaning the data, a JSON response with the error message and a 500 status code is returned.
    """
    
    options = request.json
    
    try:
        result = data_service.clean_data(options)
        
        # Update session with cleaned data
        if 'data' in result:
            session['df'] = result['data'].to_json()
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/modeling', methods=['GET', 'POST'])
def modeling():
    """
    Handle the '/modeling' route for both GET and POST requests.
    GET:
        - Checks if 'file_path' is in the session.
        - Loads data from the file path stored in the session.
        - Returns a JSON response with the numeric columns of the dataframe.
    POST:
        - Expects JSON data with 'feature_columns', 'target_column', and 'test_size'.
        - Trains a linear regression model using the provided data.
        - Returns a JSON response with the training results.
    Returns:
        - JSON response with error message and status code 400 if 'file_path' is not in the session or file does not exist.
        - JSON response with numeric columns and success status for GET requests.
        - JSON response with training results for POST requests.
        - JSON response with error message and status code 500 for any exceptions.
    Raises:
        - Exception: If any error occurs during the processing of the request.
    """
    
    try:
        if 'file_path' not in session:
            return jsonify({'error': 'No data available'}), 400
            
        file_path = Path(session['file_path'])
        model_service.load_data(file_path)
        
        if not file_path.exists():
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