from flask import Flask, jsonify
from .extensions import db, cors, migrate, jwt, mail
from .models import User, OAuthCredentials, MediaItem, RankingSession, MediaRanking
from .services import GoogleService, LLMBasedRankingService, authenticate, fetch_media_items
from .api import auth_bp, routes_bp, register_routes
from .config import Config

def create_app(config_class=Config):
    """Create and configure the Flask application"""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    cors.init_app(app, resources={r"/api/*": {
        "origins": app.config['CORS_ORIGINS'],
        "supports_credentials": True,
        "allow_headers": ["Content-Type", "Authorization"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    }})
    migrate.init_app(app, db)
    
    # Configure JWT
    app.config['JWT_SECRET_KEY'] = Config.SECRET_KEY
    app.config['JWT_TOKEN_LOCATION'] = ['headers']
    app.config['JWT_HEADER_NAME'] = 'Authorization'
    app.config['JWT_HEADER_TYPE'] = 'Bearer'
    app.config['JWT_ERROR_MESSAGE_KEY'] = 'message'
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 86400  # 24 hours
    
    @jwt.invalid_token_loader
    def invalid_token_callback(error_string):
        return jsonify({
            'message': 'Invalid token',
            'error': error_string
        }), 401

    @jwt.unauthorized_loader
    def unauthorized_callback(error_string):
        return jsonify({
            'message': 'Missing token',
            'error': error_string
        }), 401

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({
            'message': 'Token has expired',
            'error': 'token_expired'
        }), 401

    jwt.init_app(app)
    mail.init_app(app)

    # Register blueprints
    app.register_blueprint(auth_bp)

    # Register routes
    register_routes(app)

    return app

__all__ = [
    # Extensions
    'db', 'cors', 'migrate', 'jwt', 'mail',
    
    # Models
    'User', 'OAuthCredentials', 'MediaItem', 'RankingSession', 'MediaRanking',
    
    # Services
    'GoogleService', 'LLMBasedRankingService', 'authenticate', 'fetch_media_items',
    
    # API
    'auth_bp', 'routes_bp', 'register_routes',
    
    # App factory
    'create_app'
]
