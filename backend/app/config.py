import os
from dotenv import load_dotenv
import secrets

# Load environment variables from .env file
load_dotenv()

def generate_secret_key():
    """Generate a random secret key and store it in .env file if it doesn't exist."""
    if not os.getenv('SECRET_KEY'):
        # Generate a random 32-byte hex string
        secret_key = secrets.token_hex(32)
        
        # Read the current .env file
        with open('.env', 'r') as f:
            env_content = f.read()
        
        # Add or update the SECRET_KEY
        if 'SECRET_KEY=' in env_content:
            # Replace existing SECRET_KEY
            env_content = env_content.replace('SECRET_KEY=your-secret-key-here', f'SECRET_KEY={secret_key}')
        else:
            # Add new SECRET_KEY
            env_content += f'\nSECRET_KEY={secret_key}'
        
        # Write back to .env file
        with open('.env', 'w') as f:
            f.write(env_content)
        
        return secret_key
    
    return os.getenv('SECRET_KEY')

class Config:
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
    GOOGLE_AUTH_SCOPES = os.getenv('GOOGLE_AUTH_SCOPES')

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