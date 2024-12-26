from flask import Flask, jsonify
import logging
from logging.handlers import RotatingFileHandler
import os
from app.utils.exceptions import DataProcessingError, ValidationError
from app.utils.json_encoder import CustomJSONProvider

def register_error_handlers(app):
    @app.errorhandler(ValidationError)
    def handle_validation_error(error):
        return jsonify({'error': str(error)}), 400
        
    @app.errorhandler(DataProcessingError)
    def handle_processing_error(error):
        return jsonify({'error': str(error)}), 500
        
    @app.errorhandler(404)
    def handle_not_found(error):
        return jsonify({'error': 'Resource not found'}), 404
        
    @app.errorhandler(500)
    def handle_server_error(error):
        return jsonify({'error': 'Internal server error'}), 500

def create_app():
    app = Flask(__name__, 
        static_folder='static',
        template_folder='templates'
    )
    app.json = CustomJSONProvider(app)
    os.makedirs('instance', exist_ok=True)
    # Register error handlers
    register_error_handlers(app)
    
    if not os.path.exists('logs'):
        os.mkdir('logs')
    
    file_handler = RotatingFileHandler(
        'logs/yugen.log',
        maxBytes=10240,
        backupCount=10
    )
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    ))
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    
    app.secret_key = 'secret-key'
    
    from app.routes import data_routes
    app.register_blueprint(data_routes.bp)
    
    app.logger.info('Yugen startup')
    return app