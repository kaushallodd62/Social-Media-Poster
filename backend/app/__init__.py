from flask import Flask, jsonify
from .extensions import db, cors, migrate, jwt, mail, init_extensions
from .models import User, OAuthCredentials, MediaItem, RankingSession, MediaRanking
from .services import GoogleService, LLMBasedRankingService
from .api import auth_bp, routes_bp
from .config import Config
from typing import Type
import logging

logger = logging.getLogger(__name__)

def create_app(config_class: Type[Config] = Config) -> Flask:
    """
    Create and configure the Flask application.
    Args:
        config_class (Type[Config]): The configuration class to use.
    Returns:
        Flask: The configured Flask application instance.
    """
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    init_extensions(app)
    
    # Configure JWT
    app.config['JWT_SECRET_KEY'] = Config.SECRET_KEY
    app.config['JWT_TOKEN_LOCATION'] = ['headers']
    app.config['JWT_HEADER_NAME'] = 'Authorization'
    app.config['JWT_HEADER_TYPE'] = 'Bearer'
    app.config['JWT_ERROR_MESSAGE_KEY'] = 'message'
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 86400  # 24 hours
    
    @jwt.invalid_token_loader
    def invalid_token_callback(error_string: str):
        """Callback for invalid JWT token."""
        return jsonify({
            'message': 'Invalid token',
            'error': error_string
        }), 401

    @jwt.unauthorized_loader
    def unauthorized_callback(error_string: str):
        """Callback for missing JWT token."""
        return jsonify({
            'message': 'Missing token',
            'error': error_string
        }), 401

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header: dict, jwt_payload: dict):
        """Callback for expired JWT token."""
        return jsonify({
            'message': 'Token has expired',
            'error': 'token_expired'
        }), 401

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(routes_bp)

    # Register CLI commands
    with app.app_context():
        from flask_migrate import Migrate
        migrate = Migrate(app, db)
    logger.info("Flask app created and configured.")
    return app

__all__ = [
    # Extensions
    'db', 'cors', 'migrate', 'jwt', 'mail',
    
    # Models
    'User', 'OAuthCredentials', 'MediaItem', 'RankingSession', 'MediaRanking',
    
    # Services
    'GoogleService', 'LLMBasedRankingService',
]
