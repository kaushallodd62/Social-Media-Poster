from app.extensions import db
from datetime import datetime
from typing import Optional, List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class OAuthCredentials(db.Model):
    """
    SQLAlchemy model for storing OAuth credentials for a user and provider.
    """
    __tablename__ = "oauth_credentials"
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    provider = db.Column(db.String(50), nullable=False)  # e.g., 'google'
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

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert credentials object to dictionary.
        Returns:
            dict: Dictionary representation of the credentials.
        """
        return {
            'id': self.id,
            'user_id': self.user_id,
            'provider': self.provider,
            'provider_user_id': self.provider_user_id,
            'token_type': self.token_type,
            'token_expires_at': self.token_expires_at.isoformat() if self.token_expires_at else None,
            'scope': self.scope,
            'scopes': self.get_scopes(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def get_scopes(self) -> List[str]:
        """
        Get scopes as a list.
        Returns:
            list: List of scopes.
        """
        if self.scope:
            return [s for s in self.scope.split() if s]
        return []

    def set_scopes(self, scopes: Optional[List[str]]) -> None:
        """
        Set scopes from a list. Raises ValueError if required scopes are missing.
        Args:
            scopes (list): List of scopes to set.
        Raises:
            ValueError: If required scopes are missing.
        """
        if not scopes:
            self.scope = None
            return
        required_scopes = [
            'openid',
            'https://www.googleapis.com/auth/userinfo.email',
            'https://www.googleapis.com/auth/userinfo.profile'
        ]
        scopes_set = set(scopes)
        required_set = set(required_scopes)
        missing_scopes = required_set - scopes_set
        if missing_scopes:
            logger.error(f"Missing required scopes: {', '.join(missing_scopes)}")
            raise ValueError(f"Missing required scopes: {', '.join(missing_scopes)}")
        self.scope = ' '.join(s.strip() for s in scopes if s.strip())
