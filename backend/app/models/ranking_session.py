from app.extensions import db
from datetime import datetime
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

class RankingSession(db.Model):
    """
    SQLAlchemy model for a ranking session, representing a user's image ranking process.
    """
    __tablename__ = "ranking_sessions"
    
    id = db.Column(db.BigInteger, primary_key=True)
    user_id = db.Column(db.BigInteger, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    initiated_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now())
    completed_at = db.Column(db.DateTime(timezone=True))
    method = db.Column(db.String(100))  # e.g. 'ai_ranking', 'manual_ranking'
    status = db.Column(db.String(20), default='pending')  # pending, completed, failed
    error_message = db.Column(db.Text)  # For storing error details if status is failed
    created_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now())
    updated_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now(), onupdate=db.func.now())

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert ranking session to dictionary.
        Returns:
            dict: Dictionary representation of the ranking session.
        """
        return {
            'id': self.id,
            'user_id': self.user_id,
            'initiated_at': self.initiated_at.isoformat() if self.initiated_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'method': self.method,
            'status': self.status,
            'error_message': self.error_message,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
