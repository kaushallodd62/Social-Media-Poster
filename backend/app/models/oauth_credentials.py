from app.extensions import db
from datetime import datetime

class OAuthCredentials(db.Model):
    __tablename__ = "oauth_credentials"
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    provider = db.Column(db.String(50), nullable=False)  # e.g., 'google', 'google_photos'
    provider_user_id = db.Column(db.String(255))
    access_token = db.Column(db.Text, nullable=False)
    refresh_token = db.Column(db.Text)
    token_type = db.Column(db.String(50), default='Bearer')
    id_token = db.Column(db.Text)  # For Google OAuth
    token_expires_at = db.Column(db.DateTime)
    scope = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint("user_id", "provider", name="uq_user_provider"),
    )

    def to_dict(self):
        """Convert credentials object to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'provider': self.provider,
            'provider_user_id': self.provider_user_id,
            'token_type': self.token_type,
            'token_expires_at': self.token_expires_at.isoformat() if self.token_expires_at else None,
            'scope': self.scope,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def get_scopes(self):
        """Get scopes as a list"""
        return self.scope.split() if self.scope else []

    def set_scopes(self, scopes):
        """Set scopes from a list"""
        if not scopes:
            self.scope = None
            return
            
        # Ensure all required scopes are present
        required_scopes = [
            'openid',
            'https://www.googleapis.com/auth/userinfo.email',
            'https://www.googleapis.com/auth/userinfo.profile',
            'https://www.googleapis.com/auth/photoslibrary.readonly'
        ]
        
        # Convert to sets for easier comparison
        scopes_set = set(scopes)
        required_set = set(required_scopes)
        
        # Check if all required scopes are present
        missing_scopes = required_set - scopes_set
        if missing_scopes:
            raise ValueError(f"Missing required scopes: {', '.join(missing_scopes)}")
            
        self.scope = ' '.join(scopes) 