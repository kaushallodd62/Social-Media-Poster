from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_mail import Mail
from flask import Flask
from typing import Any
import logging

logger = logging.getLogger(__name__)

# Initialize extensions
db = SQLAlchemy()
cors = CORS()
migrate = Migrate()
jwt = JWTManager()
mail = Mail()

def init_extensions(app: Flask) -> None:
    """
    Initialize all Flask extensions with the app.
    Args:
        app (Flask): The Flask application instance.
    """
    db.init_app(app)
    
    # Configure CORS
    cors_config = {
        "origins": app.config['CORS_ORIGINS'],
        "supports_credentials": True,
        "allow_headers": [
            "Content-Type",
            "Authorization",
            "X-Requested-With",
            "Accept",
            "Origin",
            "Access-Control-Request-Method",
            "Access-Control-Request-Headers"
        ],
        "expose_headers": ["Content-Type", "Authorization"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "max_age": 3600  # Cache preflight requests for 1 hour
    }
    
    # In development, allow all origins
    if app.config['FLASK_ENV'] == 'development':
        # Allow both localhost:3000 and localhost:5001 (Docker mapped port)
        cors_config["origins"] = [
            "http://localhost:3000",
            "http://localhost:5001",
            "http://127.0.0.1:3000",
            "http://127.0.0.1:5001"
        ]
        cors_config["supports_credentials"] = True
    
    cors.init_app(app, resources={r"/api/*": cors_config})
    
    migrate.init_app(app, db)
    jwt.init_app(app)
    mail.init_app(app)
