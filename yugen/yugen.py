from flask import Flask, render_template, request, redirect, url_for, jsonify
import pandas as pd
import os

app = Flask(__name__)

# Create a variable to store the DataFrame
data = None

# Set upload folder
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    global data
    # Check if the POST request has the file part
    if 'file' not in request.files:
        return redirect(url_for('index'))
    
    file = request.files['file']
    
    # If the user does not select a file, the browser submits an empty file
    if file.filename == '':
        return redirect(url_for('index'))
    
    # Save the file and read it into a DataFrame
    if file:
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)
        # Reading the CSV into a pandas DataFrame
        data = pd.read_csv(filepath)
        return render_template('index.html', message="File successfully uploaded")

@app.route('/data-info')
def data_info():
    global data
    if data is None:
        return jsonify({"error": "No data available"}), 400
    
    # Provide basic information like rows, columns, and column names
    data_info = {
        'rows': data.shape[0],
        'columns': data.shape[1],
        'column_names': data.columns.tolist()
    }
    return jsonify(data_info)

if __name__ == '__main__':
    app.run(debug=True)