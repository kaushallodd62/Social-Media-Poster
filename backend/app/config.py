import os
from dotenv import load_dotenv
import secrets
import logging
from typing import Optional, List, Dict, Any

# Load environment variables from .env file
load_dotenv()

logger = logging.getLogger(__name__)

def generate_secret_key() -> str:
    """
    Generate a random secret key and store it in .env file if it doesn't exist.
    Returns:
        str: The secret key.
    """
    if not os.getenv('SECRET_KEY'):
        secret_key = secrets.token_hex(32)
        try:
            with open('.env', 'r') as f:
                env_content = f.read()
            if 'SECRET_KEY=' in env_content:
                env_content = env_content.replace('SECRET_KEY=your-secret-key-here', f'SECRET_KEY={secret_key}')
            else:
                env_content += f'\nSECRET_KEY={secret_key}'
            with open('.env', 'w') as f:
                f.write(env_content)
            logger.info("Generated and stored new SECRET_KEY in .env file.")
        except Exception as e:
            logger.error(f"Failed to generate/store SECRET_KEY: {str(e)}", exc_info=True)
            raise
        return secret_key
    return os.getenv('SECRET_KEY')

class Config:
    """
    Configuration class for Flask app, database, OAuth, CORS, logging, and email.
    """
    # Flask Configuration
    SECRET_KEY = generate_secret_key()
    FLASK_APP = os.getenv('FLASK_APP', 'app.py')
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    FLASK_DEBUG = os.getenv('FLASK_DEBUG', '1') == '1'

    # Database Configuration
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Google OAuth Configuration
    GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
    GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
    GOOGLE_REDIRECT_URI = os.getenv('GOOGLE_REDIRECT_URI')

    # CORS Configuration
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:3000').split(',')
    FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost:3000')

    # Logging Configuration
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'app.log')

    # Cohere API Key
    COHERE_API_KEY = os.getenv('COHERE_API_KEY')

    # Email Configuration
    MAIL_SERVER = os.getenv('SMTP_HOST')
    MAIL_PORT = int(os.getenv('SMTP_PORT', '587'))
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.getenv('SMTP_USERNAME')
    MAIL_PASSWORD = os.getenv('SMTP_PASSWORD')
    MAIL_DEFAULT_SENDER = os.getenv('SMTP_USERNAME') 