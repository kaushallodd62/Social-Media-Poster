from app.extensions import db
from datetime import datetime, timedelta
import jwt
from app.config import Config
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    __tablename__ = "users"
    
    id = db.Column(db.BigInteger, primary_key=True)
    email = db.Column(db.String(320), unique=True, nullable=False)
    password_hash = db.Column(db.String(255))
    display_name = db.Column(db.String(100))
    profile_picture = db.Column(db.String(500))
    is_active = db.Column(db.Boolean, default=True)
    is_verified = db.Column(db.Boolean, default=False)
    verification_token = db.Column(db.String(100), unique=True)
    reset_password_token = db.Column(db.String(100), unique=True)
    reset_password_expires = db.Column(db.DateTime(timezone=True))
    created_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now())
    updated_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now(), onupdate=db.func.now())

    def set_password(self, password):
        """Set user password"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Check user password"""
        return check_password_hash(self.password_hash, password)

    def generate_auth_token(self):
        """Generate JWT token"""
        payload = {
            'user_id': self.id,
            'email': self.email,
            'exp': datetime.utcnow() + timedelta(days=1)
        }
        return jwt.encode(payload, Config.SECRET_KEY, algorithm='HS256')

    @staticmethod
    def verify_auth_token(token):
        """Verify JWT token"""
        try:
            payload = jwt.decode(token, Config.SECRET_KEY, algorithms=['HS256'])
            return User.query.get(payload['user_id'])
        except:
            return None

    def to_dict(self):
        """Convert user object to dictionary"""
        return {
            'id': self.id,
            'email': self.email,
            'display_name': self.display_name,
            'profile_picture': self.profile_picture,
            'is_verified': self.is_verified,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        } 