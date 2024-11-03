from flask import Flask
import logging
from logging import setup_logging
from logging.handlers import RotatingFileHandler
import os

def create_app():
    app = Flask(__name__)
    setup_logging()
    register_error_handlers(app)
    
    if not os.path.exists('logs'):
        os.mkdir('logs')
    
    file_handler = RotatingFileHandler(
        'logs/yugen.log',
        maxBytes=10240,
        backupCount=10
    )
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s'
    ))
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    
    from app.routes import data_routes
    app.register_blueprint(data_routes.bp)
    
    app.logger.info('Yugen startup')
    return app