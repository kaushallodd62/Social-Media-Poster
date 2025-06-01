from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_mail import Mail

# Initialize extensions
db = SQLAlchemy()
cors = CORS()
migrate = Migrate()
jwt = JWTManager()
mail = Mail()

def init_extensions(app):
    """Initialize all Flask extensions with the app"""
    db.init_app(app)
    cors.init_app(app, resources={r"/api/*": {
        "origins": app.config['CORS_ORIGINS'],
        "supports_credentials": True,
        "allow_headers": ["Content-Type", "Authorization"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    }})
    migrate.init_app(app, db)
    jwt.init_app(app)
    mail.init_app(app)
