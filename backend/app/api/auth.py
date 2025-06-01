from flask import Blueprint, request, jsonify, redirect, url_for, g
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

auth_bp = Blueprint('auth', __name__)
google_service = GoogleService()

def generate_token(length=32):
    """Generate a random token of specified length."""
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        auth_header = request.headers.get('Authorization')
        
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
        
        if not token:
            return jsonify({'message': 'Token is missing'}), 401
        
        try:
            user = User.verify_auth_token(token)
            if not user:
                return jsonify({'message': 'Invalid token'}), 401
            g.current_user = user
        except Exception:
            return jsonify({'message': 'Invalid token'}), 401
            
        return f(*args, **kwargs)
    return decorated

# Google OAuth Routes
@auth_bp.route('/api/auth/google/url', methods=['GET'])
def get_google_auth_url():
    """Get Google OAuth URL for login"""
    try:
        url = google_service.get_auth_url(
            scopes=[
                'openid',
                'https://www.googleapis.com/auth/userinfo.email',
                'https://www.googleapis.com/auth/userinfo.profile'
            ],
            access_type='offline',
            include_granted_scopes='false'
        )
        return jsonify({'url': url})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/api/auth/google/callback', methods=['GET'])
def google_callback():
    """Handle Google OAuth callback"""
    try:
        # Get authorization code from request
        code = request.args.get('code')
        state = request.args.get('state')  # For CSRF protection
        
        if not code:
            return redirect(
                f"{Config.FRONTEND_URL}/auth/callback?error=No code provided"
            )

        # Exchange code for tokens and get user info
        tokens = google_service.get_tokens(
            auth_code=code,
            scopes=[
                'openid',
                'https://www.googleapis.com/auth/userinfo.email',
                'https://www.googleapis.com/auth/userinfo.profile'
            ]
        )
        if not tokens or not tokens.get('access_token'):
            return redirect(
                f"{Config.FRONTEND_URL}/auth/callback?error=Failed to get access token"
            )

        try:
            user_info = google_service.get_user_info(tokens['access_token'])
        except Exception as e:
            return redirect(
                f"{Config.FRONTEND_URL}/auth/callback?error=Failed to get user info: {str(e)}"
            )

        # Get or create user
        user = User.query.filter_by(email=user_info['email']).first()
        if not user:
            # Create new user
            user = User(
                email=user_info['email'],
                display_name=user_info.get('name', user_info['email'].split('@')[0]),
                is_verified=user_info.get('verified_email', False),
                profile_picture=user_info.get('picture')
            )
            db.session.add(user)
            db.session.flush()

        # Store OAuth credentials
        oauth_cred = OAuthCredentials.query.filter_by(
            user_id=user.id,
            provider='google'
        ).first()
        
        if not oauth_cred:
            oauth_cred = OAuthCredentials(
                user_id=user.id,
                provider='google',
                provider_user_id=user_info['id']
            )
        
        oauth_cred.access_token = tokens['access_token']
        oauth_cred.refresh_token = tokens.get('refresh_token')
        oauth_cred.token_type = tokens.get('token_type') # Google always returns Bearer
        oauth_cred.token_expires_at = (
            datetime.fromtimestamp(tokens.get('expires_in'))
            if tokens.get('expires_in') else None
        )
        
        db.session.add(oauth_cred)
        db.session.commit()

        # Create access and refresh tokens
        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)

        # Redirect to frontend with tokens
        return redirect(
            f"{Config.FRONTEND_URL}/auth/callback?token={access_token}&refresh_token={refresh_token}"
        )

    except Exception as e:
        db.session.rollback()
        error_message = str(e).replace('\n', ' ').strip()  # Remove newlines and extra whitespace
        return redirect(f"{Config.FRONTEND_URL}/auth/callback?error={error_message}")

# Email/Password Authentication Routes
@auth_bp.route('/api/auth/register', methods=['POST'])
def register():
    """Register a new user"""
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
        return jsonify({'message': str(e)}), 500

@auth_bp.route('/api/auth/login', methods=['POST'])
def login():
    """Login with email and password"""
    try:
        data = request.get_json()
        
        if not data or not data.get('email') or not data.get('password'):
            return jsonify({'message': 'Missing required fields'}), 400
            
        user = User.query.filter_by(email=data['email']).first()
        
        if not user or not user.check_password(data['password']):
            return jsonify({'message': 'Invalid email or password'}), 401
            
        if not user.is_verified:
            return jsonify({'message': 'Please verify your email first'}), 401
            
        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)
        
        return jsonify({
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': {
                'id': user.id,
                'email': user.email,
                'display_name': user.display_name
            }
        })
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@auth_bp.route('/api/auth/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Refresh access token"""
    try:
        user_id = get_jwt_identity()
        access_token = create_access_token(identity=user_id)
        return jsonify({'access_token': access_token})
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@auth_bp.route('/api/auth/verify-email/<token>', methods=['GET'])
def verify_email(token):
    """Verify user email"""
    try:
        user = User.query.filter_by(verification_token=token).first()
        
        if not user:
            return jsonify({'message': 'Invalid verification token'}), 400
            
        user.is_verified = True
        user.verification_token = None
        db.session.commit()
        
        return jsonify({'message': 'Email verified successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': str(e)}), 500

@auth_bp.route('/api/auth/forgot-password', methods=['POST'])
def forgot_password():
    """Request password reset"""
    try:
        data = request.get_json()
        
        if not data or not data.get('email'):
            return jsonify({'message': 'Email is required'}), 400
            
        user = User.query.filter_by(email=data['email']).first()
        
        if user:
            user.reset_password_token = generate_token()
            user.reset_password_expires = datetime.utcnow() + timedelta(hours=1)
            db.session.commit()
            # TODO: Send password reset email
            
        return jsonify({
            'message': 'If your email is registered, you will receive password reset instructions'
        })
    except Exception as e:
        db.session.rollback()
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

# Google Photos Integration Routes
@auth_bp.route('/api/auth/google/photos/url', methods=['GET'])
@jwt_required()
def get_google_photos_auth_url():
    """Get Google OAuth URL for Photos access"""
    try:
        url = google_service.get_auth_url(
            scopes=['https://www.googleapis.com/auth/photoslibrary.readonly'],
            access_type='offline',
            include_granted_scopes='true'
        )
        return jsonify({'url': url})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/api/auth/google/photos/callback', methods=['GET'])
@jwt_required()
def google_photos_callback():
    """Handle Google Photos OAuth callback"""
    try:
        user_id = get_jwt_identity()
        code = request.args.get('code')
        if not code:
            return redirect(
                url_for('frontend.photos', error='No code provided')
            )

        # Exchange code for tokens
        tokens = google_service.get_tokens(
            code,
            scopes=['https://www.googleapis.com/auth/photoslibrary.readonly']
        )
        
        # Store tokens in database
        user = User.query.get(user_id)
        if not user:
            return redirect(url_for('frontend.photos', error='User not found'))

        # Store tokens in oauth_credentials table
        google_service.store_credentials(user_id, 'google_photos', tokens)

        return redirect(url_for('frontend.photos'))

    except Exception as e:
        return redirect(url_for('frontend.photos', error=str(e))) 