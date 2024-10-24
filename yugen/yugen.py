from flask import Flask, render_template, request, jsonify
import pandas as pd
import tempfile
from utils.data_processing import load_data, get_data_info, profile_data

app = Flask(__name__)

# Global variable to hold the file path of the temporary DataFrame
dataframe_filepath = None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    global dataframe_filepath
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded.'})
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file.'})

    # Load the data into a DataFrame
    dataframe = load_data(file)
    if dataframe is None:
        return jsonify({'error': 'Failed to read the file.'})

    # Save the DataFrame to a temporary CSV file
    dataframe_filepath = save_dataframe(dataframe)

    # Get data info after loading
    info = get_data_info(dataframe)

    return jsonify({
        'message': 'File uploaded successfully!',
        'info': info
    })

@app.route('/data-info', methods=['GET'])
def data_info():
    global dataframe_filepath
    if dataframe_filepath is None:
        return jsonify({'error': 'No data loaded.'})

    # Load the DataFrame from the temporary file
    df = pd.read_csv(dataframe_filepath)
    
    info = {
        'rows': df.shape[0],
        'columns': df.shape[1],
        'column_names': df.columns.tolist(),
    }
    return jsonify(info)

# Function to save DataFrame to a temporary CSV file
def save_dataframe(df):
    with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as tmp_file:
        df.to_csv(tmp_file.name, index=False)
        return tmp_file.name

@app.route('/profile', methods=['GET'])
def profile():
    global dataframe_filepath
    if dataframe_filepath is None:
        return jsonify({'error': 'No data loaded.'})

    # Load the DataFrame from the temporary file
    df = pd.read_csv(dataframe_filepath)
    
    # Call your profile_data function to get profiling information
    profiling_info = profile_data(df)
    return jsonify(profiling_info)

if __name__ == '__main__':
    app.run(debug=True)
