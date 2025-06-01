from app.extensions import db
from datetime import datetime

class OAuthCredentials(db.Model):
    __tablename__ = "oauth_credentials"
    
    id = db.Column(db.BigInteger, primary_key=True)
    user_id = db.Column(db.BigInteger, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    provider = db.Column(db.String(50), nullable=False)  # e.g., 'google', 'google_photos'
    provider_user_id = db.Column(db.String(255))
    access_token = db.Column(db.Text, nullable=False)
    refresh_token = db.Column(db.Text)
    token_type = db.Column(db.String(50), default='Bearer')
    id_token = db.Column(db.Text)  # For Google OAuth
    token_expires_at = db.Column(db.DateTime(timezone=True))
    scope = db.Column(db.Text)
    created_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now())
    updated_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now(), onupdate=db.func.now())

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