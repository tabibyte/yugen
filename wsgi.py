from app import create_app
import webbrowser
import threading
import time

app = create_app()

def open_browser():
    time.sleep(1.5)
    webbrowser.open('http://127.0.0.1:5000/')

if __name__ == '__main__':
    threading.Thread(target=open_browser).start()
    app.run(debug=True)