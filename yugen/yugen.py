from flask import Flask, render_template, request, jsonify
import pandas as pd
from utils.data_processing import load_csv, get_data_info, profile_data, save_dataframe

app = Flask(__name__)


# global variable that holds imported dataframes path to work with
dataframe_filepath = None


# rendering index.html
@app.route('/')
def index():
    return render_template('index.html')


# handling upload
@app.route('/upload', methods=['POST'])
def upload_file():
    
    # get the dataframe path
    global dataframe_filepath
    
    # handling errors
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded.'})

    # http request to get the file
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No selected file.'})

    # create a dataframe of the data / data_processing.py -> def load_data()
    dataframe = load_csv(file)
    
    if dataframe is None:
        return jsonify({'error': 'Failed to read the file.'})

    # get the temporary saved dataframes file path
    dataframe_filepath = save_dataframe(dataframe)

    # read the data and get the upload info
    info = get_data_info(dataframe)
    return jsonify({
        'message': 'File uploaded successfully!',
        'info': info
    })


# handling getting info
@app.route('/data-info', methods=['GET'])
def data_info():
    
    # get the dataframe path
    global dataframe_filepath
    
    if dataframe_filepath is None:
        return jsonify({'error': 'No data loaded.'})

    # read the data and get the info
    df = pd.read_csv(dataframe_filepath)
    info = {
        'rows': df.shape[0],
        'columns': df.shape[1],
        'column_names': df.columns.tolist(),
    }
    return jsonify(info)


# handling profiling
@app.route('/profile', methods=['GET'])
def profile():
    
    # get the dataframe path
    global dataframe_filepath
    
    if dataframe_filepath is None:
        return jsonify({'error': 'No data loaded.'})
    
    # read the data as dataframe from file path and get the profiling info
    df = pd.read_csv(dataframe_filepath)
    profiling_info = profile_data(df)
    return jsonify(profiling_info)


if __name__ == '__main__':
    app.run(debug=True)
