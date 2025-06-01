from flask import Flask
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
    cors.init_app(app, resources={r"/api/*": {"origins": app.config['CORS_ORIGINS']}})
    migrate.init_app(app, db)
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
