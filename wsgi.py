from app import create_app
import webbrowser
import time
import os

app = create_app()

if __name__ == '__main__':
    if not os.environ.get('VSCODE_PID'):
        webbrowser.open('http://127.0.0.1:5000/')
    app.run(debug=True)