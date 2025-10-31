# -*- coding: utf-8 -*-

from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from backend.models import db
from backend.config import config
import os

def create_app(config_name='development'):
    """
    Application factory function
    Creates and configures the Flask application
    """
    
    # Initialize Flask app
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config[config_name])
    
    # Initialize database
    db.init_app(app)
    
    # Enable CORS (allow frontend origin and cookies in development)
    CORS(
        app,
        supports_credentials=True,
        resources={
            r"/api/*": {
                "origins": [
                    "http://127.0.0.1:5500",
                    "http://localhost:5500",
                    "http://127.0.0.1:8000",
                    "http://localhost:8000",
                ]
            }
        },
    )
    
    # Create database tables if they don't exist
    with app.app_context():
        db.create_all()
    
    # Register blueprints (we'll create these next)
    from backend.routes.auth_routes import auth_bp
    from backend.routes.ticket_routes import ticket_bp
    from backend.routes.user_routes import user_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(ticket_bp, url_prefix='/api/tickets')
    app.register_blueprint(user_bp, url_prefix='/api/users')
    
    # Health check endpoint (useful for monitoring if app is running)
    @app.route('/api/health', methods=['GET'])
    def health_check():
        return jsonify({
            'status': 'healthy',
            'message': 'Ticketing system is running'
        }), 200
    
    # Root endpoint
    @app.route('/', methods=['GET'])
    def root():
        return jsonify({
            'message': 'IT Help Desk Ticketing System API',
            'version': '1.0.0',
            'endpoints': {
                'health': '/api/health',
                'auth': '/api/auth',
                'tickets': '/api/tickets',
                'users': '/api/users'
            }
        }), 200

    # Serve frontend files directly from Flask for same-origin dev
    frontend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'frontend'))

    @app.route('/login.html')
    def serve_login():
        return send_from_directory(frontend_dir, 'login.html')

    @app.route('/dashboard.html')
    def serve_dashboard():
        return send_from_directory(frontend_dir, 'dashboard.html')
    
    return app


if __name__ == '__main__':
    # Get environment from environment variable, default to development
    env = os.environ.get('FLASK_ENV', 'development')
    
    # Create app with specified environment
    app = create_app(env)
    
    # Run the application
    print("Starting IT Help Desk Ticketing System...")
    print(f"Environment: {env}")
    print("Server running on http://127.0.0.1:5000")
    
    app.run(host='0.0.0.0', port=5000, debug=True)
