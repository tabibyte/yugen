from app import create_app
import webbrowser
import time
import os

app = create_app()

def open_browser():
    webbrowser.open('http://127.0.0.1:5000/')

if __name__ == '__main__':
    if not os.environ.get('VSCODE_PID'):
        if os.environ.get('WERKZEUG_RUN_MAIN') != 'true':
            open_browser()
    app.run(debug=True)