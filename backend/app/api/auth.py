from flask import Blueprint, request, jsonify, redirect, url_for, g, make_response
from flask_jwt_extended import (
    create_access_token, jwt_required, get_jwt_identity, create_refresh_token
)
from werkzeug.security import generate_password_hash, check_password_hash
from app.services.google_service import GoogleService
from app.models.user import User
from app.models.oauth_credentials import OAuthCredentials
from app.extensions import db, jwt
from datetime import datetime, timedelta
import secrets
import string
from functools import wraps
from app.config import Config
import logging
from typing import Optional, List, Dict, Any

logger = logging.getLogger(__name__)

auth_bp = Blueprint('auth', __name__)
google_service = GoogleService()

def generate_token(length: int = 32) -> str:
    """
    Generate a random token of specified length.

    Args:
        length (int): Length of the token.
    Returns:
        str: The generated token.
    """
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def token_required(f):
    """
    Decorator to require a valid token for a route.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
        if not token:
            logger.warning('Token is missing in request header.')
            return jsonify({'message': 'Token is missing'}), 401
        try:
            user = User.verify_auth_token(token)
            if not user:
                logger.warning('Invalid token provided.')
                return jsonify({'message': 'Invalid token'}), 401
            g.current_user = user
        except Exception as e:
            logger.warning(f'Exception during token verification: {str(e)}')
            return jsonify({'message': 'Invalid token'}), 401
        return f(*args, **kwargs)
    return decorated

# Google OAuth Routes
@auth_bp.route('/api/auth/google/url', methods=['GET'])
def get_google_auth_url() -> Any:
    """
    Get Google OAuth URL for login.
    Returns:
        JSON response with the OAuth URL or error.
    """
    try:
        url = google_service.get_auth_url(
            access_type='offline',
            include_granted_scopes=True
        )
        return jsonify({'url': url})
    except Exception as e:
        logger.error(f"Failed to generate Google OAuth URL: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/api/auth/google/callback', methods=['GET'])
def google_callback() -> Any:
    """
    Handle Google OAuth callback.
    Returns:
        Redirect response to frontend with token or error.
    """
    try:
        code = request.args.get('code')
        if not code:
            logger.warning('No code provided in Google OAuth callback.')
            return redirect(f"{Config.FRONTEND_URL}/auth/callback#error=No code provided")
        tokens = google_service.get_tokens(code)
        if not tokens or not tokens.get('access_token'):
            logger.warning('Failed to get access token from Google.')
            return redirect(f"{Config.FRONTEND_URL}/auth/callback#error=Failed to get access token")
        try:
            user_info = google_service.get_user_info(tokens['access_token'])
        except Exception as e:
            logger.error(f"Failed to get user info from Google: {str(e)}", exc_info=True)
            return redirect(f"{Config.FRONTEND_URL}/auth/callback#error=Failed to get user info: {str(e)}")
        user = User.query.filter_by(email=user_info['email']).first()
        if not user:
            user = User(
                email=user_info['email'],
                display_name=user_info.get('name', user_info['email'].split('@')[0]),
                is_verified=user_info.get('verified_email', False),
                profile_picture=user_info.get('picture')
            )
            db.session.add(user)
            db.session.flush()
            logger.info(f"Created new user via Google OAuth: {user.email}")
        google_service.store_credentials(user.id, 'google', tokens)
        access_token = create_access_token(identity=user.id, expires_delta=timedelta(hours=1))
        refresh_token = create_refresh_token(identity=user.id, expires_delta=timedelta(days=7))
        response = make_response(redirect(f"{Config.FRONTEND_URL}/auth/callback#token={access_token}"))
        response.set_cookie(
            'refresh_token',
            refresh_token,
            httponly=True,
            secure=True,
            samesite='Lax',
            max_age=7*24*60*60,
            path='/api/auth/refresh'
        )
        logger.info(f"User {user.email} logged in via Google OAuth.")
        return response
    except Exception as e:
        db.session.rollback()
        error_message = str(e).replace('\n', ' ').strip()
        logger.error(f"Google OAuth callback failed: {error_message}", exc_info=True)
        return redirect(f"{Config.FRONTEND_URL}/auth/callback#error={error_message}")

# Email/Password Authentication Routes
@auth_bp.route('/api/auth/register', methods=['POST'])
def register() -> Any:
    """
    Register a new user.
    Returns:
        JSON response with user info or error.
    """
    try:
        data = request.get_json()
        if not data or not data.get('email') or not data.get('password'):
            return jsonify({'message': 'Missing required fields'}), 400
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'message': 'Email already registered'}), 400
        user = User(
            email=data['email'],
            display_name=data.get('display_name', ''),
            is_verified=False
        )
        user.set_password(data['password'])
        user.verification_token = generate_token()
        db.session.add(user)
        db.session.commit()
        logger.info(f"User registered: {user.email}")
        # TODO: Send verification email
        return jsonify({
            'message': 'Registration successful. Please check your email to verify your account.',
            'user': {
                'id': user.id,
                'email': user.email,
                'display_name': user.display_name
            }
        }), 201
    except Exception as e:
        db.session.rollback()
        logger.error(f"User registration failed: {str(e)}", exc_info=True)
        return jsonify({'message': str(e)}), 500

@auth_bp.route('/api/auth/login', methods=['POST'])
def login() -> Any:
    """
    Login with email and password.
    Returns:
        JSON response with access token and user info or error.
    """
    try:
        data = request.get_json()
        if not data or not data.get('email') or not data.get('password'):
            return jsonify({'message': 'Missing required fields'}), 400
        user = User.query.filter_by(email=data['email']).first()
        if not user or not user.check_password(data['password']):
            logger.warning(f"Failed login attempt for email: {data.get('email')}")
            return jsonify({'message': 'Invalid email or password'}), 401
        if not user.is_verified:
            logger.warning(f"Unverified user login attempt: {user.email}")
            return jsonify({'message': 'Please verify your email first'}), 401
        access_token = create_access_token(identity=user.id, expires_delta=timedelta(hours=1))
        refresh_token = create_refresh_token(identity=user.id, expires_delta=timedelta(days=7))
        response = jsonify({
            'access_token': access_token,
            'user': {
                'id': user.id,
                'email': user.email,
                'display_name': user.display_name
            }
        })
        response.set_cookie(
            'refresh_token',
            refresh_token,
            httponly=True,
            secure=True,
            samesite='Lax',
            max_age=7*24*60*60,
            path='/api/auth/refresh'
        )
        logger.info(f"User logged in: {user.email}")
        return response
    except Exception as e:
        logger.error(f"Login failed: {str(e)}", exc_info=True)
        return jsonify({'message': str(e)}), 500

@auth_bp.route('/api/auth/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh() -> Any:
    """
    Refresh access token.
    Returns:
        JSON response with new access token or error.
    """
    try:
        user_id = get_jwt_identity()
        access_token = create_access_token(identity=user_id)
        logger.info(f"Refreshed access token for user_id={user_id}")
        return jsonify({'access_token': access_token})
    except Exception as e:
        logger.error(f"Token refresh failed: {str(e)}", exc_info=True)
        return jsonify({'message': str(e)}), 500

@auth_bp.route('/api/auth/verify-email/<token>', methods=['GET'])
def verify_email(token: str) -> Any:
    """
    Verify user email.
    Args:
        token (str): Verification token.
    Returns:
        JSON response with success or error message.
    """
    try:
        user = User.query.filter_by(verification_token=token).first()
        if not user:
            return jsonify({'message': 'Invalid verification token'}), 400
        user.is_verified = True
        user.verification_token = None
        db.session.commit()
        logger.info(f"User email verified: {user.email}")
        return jsonify({'message': 'Email verified successfully'})
    except Exception as e:
        db.session.rollback()
        logger.error(f"Email verification failed: {str(e)}", exc_info=True)
        return jsonify({'message': str(e)}), 500

@auth_bp.route('/api/auth/forgot-password', methods=['POST'])
def forgot_password() -> Any:
    """
    Request password reset.
    Returns:
        JSON response with success message or error.
    """
    try:
        data = request.get_json()
        if not data or not data.get('email'):
            return jsonify({'message': 'Email is required'}), 400
        user = User.query.filter_by(email=data['email']).first()
        if user:
            user.reset_password_token = generate_token()
            user.reset_password_expires = datetime.utcnow() + timedelta(hours=1)
            db.session.commit()
            logger.info(f"Password reset requested for user: {user.email}")
            # TODO: Send password reset email
        return jsonify({
            'message': 'If your email is registered, you will receive password reset instructions'
        })
    except Exception as e:
        db.session.rollback()
        logger.error(f"Password reset request failed: {str(e)}", exc_info=True)
        return jsonify({'message': str(e)}), 500

@auth_bp.route('/api/auth/reset-password', methods=['POST'])
def reset_password():
    """Reset password with token"""
    try:
        data = request.get_json()
        
        if not data or not data.get('token') or not data.get('password'):
            return jsonify({'message': 'Missing required fields'}), 400
            
        user = User.query.filter_by(reset_password_token=data['token']).first()
        
        if not user or user.reset_password_expires < datetime.utcnow():
            return jsonify({'message': 'Invalid or expired reset token'}), 400
            
        user.set_password(data['password'])
        user.reset_password_token = None
        user.reset_password_expires = None
        db.session.commit()
        
        return jsonify({'message': 'Password reset successful'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 500

# User Info Routes
@auth_bp.route('/api/auth/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """Get current user info"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({
            'id': user.id,
            'email': user.email,
            'display_name': user.display_name,
            'profile_picture': user.profile_picture,
            'is_verified': user.is_verified
        })
    except Exception as e:
        return jsonify({'message': str(e)}), 500 