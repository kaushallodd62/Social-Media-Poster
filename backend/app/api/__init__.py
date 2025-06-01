from .auth import auth_bp
from .routes import routes_bp, register_routes

__all__ = [
    'auth_bp',
    'routes_bp',
    'register_routes'
]
