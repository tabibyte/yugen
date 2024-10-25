from flask import Flask, render_template, request, jsonify
import pandas as pd
from utils.data_processing import load_csv, get_data_info, profile_data, save_dataframe, clean_data, get_head
import tempfile

app = Flask(__name__)

# Global variables to hold the file paths of imported and cleaned dataframes
dataframe_filepath = None
cleaned_dataframe_filepath = None
dataframe = None  # To hold the original dataframe in memory
cleaned_dataframe = None  # To hold the cleaned dataframe in memory

# Rendering index.html
@app.route('/')
def index():
    return render_template('index.html')

# Handling file upload
@app.route('/upload', methods=['POST'])
def upload_file():
    global dataframe_filepath, dataframe

    # Handling errors
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded.'})

    # Get the uploaded file
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file.'})

    # Load the dataframe
    dataframe = load_csv(file)
    if dataframe is None:
        return jsonify({'error': 'Failed to read the file.'})

    # Save the dataframe to a temporary file
    dataframe_filepath = save_dataframe(dataframe)

    # Get the upload info
    info = get_data_info(dataframe)
    sample = get_head(dataframe)
    
    return jsonify({
        'message': 'File uploaded successfully!',
        'info': info,
        'head_data': sample
    })

# Handling getting data info
@app.route('/data-info', methods=['GET'])
def data_info():
    global dataframe_filepath

    if dataframe_filepath is None:
        return jsonify({'error': 'No data loaded.'})

    # Read the data and get the info
    df = pd.read_csv(dataframe_filepath)
    info = {
        'rows': df.shape[0],
        'columns': df.shape[1],
        'column_names': df.columns.tolist(),
    }
    return jsonify(info)

# Handling profiling
@app.route('/profile', methods=['GET'])
def profile():
    data_type = request.args.get('data_type', 'original')
    if data_type == 'cleaned':
        if cleaned_dataframe is None:
            return jsonify({'error': 'No cleaned data loaded.'})
        df = cleaned_dataframe
    else:
        if dataframe is None:
            return jsonify({'error': 'No original data loaded.'})
        df = dataframe

    profiling_info = profile_data(df)
    return jsonify(profiling_info)

# Handling data cleaning
@app.route('/clean-data', methods=['POST'])
def clean_data_route():
    global cleaned_dataframe

    if dataframe is None:
        return jsonify({'error': 'No data loaded to clean.'})
    
    cleaning_options = request.json
    cleaned_dataframe = clean_data(dataframe, cleaning_options)

    if cleaned_dataframe is None:
        return jsonify({'error': 'Cleaning operation failed.'})

    # Save cleaned data to a tempfile
    temp = tempfile.NamedTemporaryFile(delete=False, suffix='.csv')
    cleaned_dataframe.to_csv(temp.name, index=False)
    global cleaned_dataframe_filepath
    cleaned_dataframe_filepath = temp.name  # Store the cleaned dataframe filepath

    return jsonify({'message': 'Data cleaned successfully!'})

if __name__ == '__main__':
    app.run(debug=True)
