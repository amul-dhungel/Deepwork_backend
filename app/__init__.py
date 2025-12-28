"""
Flask application factory for WordAssistantAI backend.
"""

from flask import Flask, jsonify, request
from flask_cors import CORS

try:
    from flasgger import Swagger
    FLASGGER_AVAILABLE = True
except ImportError:
    FLASGGER_AVAILABLE = False
    print("Warning: Flasgger not installed. Swagger UI disabled. Install with: pip install flasgger")

from .config import Config


def create_app(config_class=Config):
    """Create and configure the Flask application."""
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize folders
    config_class.init_app()
    
    # Configure CORS - Simple and effective
    CORS(app, resources={r"/*": {"origins": "*"}})
    
    # Configure Swagger/OpenAPI Documentation (if available)
    if FLASGGER_AVAILABLE:
        swagger_config = {
            "headers": [],
            "specs": [
                {
                    "endpoint": 'apispec',
                    "route": '/apispec.json',
                    "rule_filter": lambda rule: True,
                    "model_filter": lambda tag: True,
                }
            ],
            "static_url_path": "/flasgger_static",
            "swagger_ui": True,
            "specs_route": "/api/docs"
        }
        
        # Load swagger spec from YAML file
        import os
        import yaml
        swagger_file = os.path.join(os.path.dirname(__file__), '..', 'swagger.yaml')
        
        try:
            with open(swagger_file, 'r') as f:
                swagger_template = yaml.safe_load(f)
            print(f"✅ Loaded Swagger spec from {swagger_file}")
        except Exception as e:
            print(f"⚠️  Could not load swagger.yaml: {e}")
            # Fallback to basic template
            swagger_template = {
                "swagger": "2.0",
                "info": {
                    "title": "WordAssistantAI API",
                    "description": "AI-powered document creation and editing API",
                    "version": "1.0.0"
                }
            }
        
        Swagger(app, config=swagger_config, template=swagger_template)
        print("✅ Swagger UI enabled at http://localhost:8000/api/docs")
    
    # Error handler to ensure CORS headers on errors
    @app.errorhandler(Exception)
    def handle_error(e):
        response = jsonify({'error': str(e)})
        response.status_code = getattr(e, 'code', 500)
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Session-ID'
        return response
    
    # Register blueprints
    from .routes import health_routes, file_routes, generation_routes, chat_routes, mock_routes, rag_routes, poster_routes, infographic_routes
    
    app.register_blueprint(health_routes.bp)
    app.register_blueprint(file_routes.bp)
    app.register_blueprint(generation_routes.bp)
    app.register_blueprint(chat_routes.bp)
    app.register_blueprint(mock_routes.bp)
    app.register_blueprint(rag_routes.rag_bp)  # RAG routes
    app.register_blueprint(poster_routes.bp)  # Poster routes
    app.register_blueprint(infographic_routes.infographic_bp)  # Infographic routes
    
    print("✅ RAG routes registered at /api/rag/*")
    print("✅ Poster routes registered at /api/poster/*")
    print("✅ Infographic routes registered at /api/infographic/*")

    
    return app
