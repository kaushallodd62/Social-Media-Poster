from app.extensions import db
from sqlalchemy.dialects.postgresql import JSONB, ARRAY
from datetime import datetime
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

class MediaRanking(db.Model):
    """
    SQLAlchemy model for storing the ranking of a media item in a ranking session.
    """
    __tablename__ = "media_rankings"
    
    id = db.Column(db.BigInteger, primary_key=True)
    ranking_session_id = db.Column(db.BigInteger, db.ForeignKey("ranking_sessions.id", ondelete="CASCADE"), nullable=False)
    media_item_id = db.Column(db.BigInteger, db.ForeignKey("media_items.id", ondelete="CASCADE"), nullable=False)
    technical_score = db.Column(db.Numeric(5,2))
    aesthetic_score = db.Column(db.Numeric(5,2))
    combined_score = db.Column(db.Numeric(5,2))
    llm_reasoning = db.Column(JSONB)  # For storing AI reasoning about the photo
    tags_json = db.Column(ARRAY(db.Text))
    analysis_type = db.Column(db.String(32), nullable=True)  # e.g., 'default', 'v2', etc.
    status = db.Column(db.String(20), default='completed')  # 'pending', 'completed', 'failed', etc.
    error_message = db.Column(db.Text, nullable=True)  # For failed analyses
    analyzed_at = db.Column(db.DateTime(timezone=True), nullable=True)  # When analysis completed
    created_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now())

    __table_args__ = (
        db.Index("idx_media_rankings_session_score", "ranking_session_id", "combined_score"),
    )

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert media ranking to dictionary.
        Returns:
            dict: Dictionary representation of the media ranking.
        """
        return {
            'id': self.id,
            'ranking_session_id': self.ranking_session_id,
            'media_item_id': self.media_item_id,
            'technical_score': float(self.technical_score) if self.technical_score else None,
            'aesthetic_score': float(self.aesthetic_score) if self.aesthetic_score else None,
            'combined_score': float(self.combined_score) if self.combined_score else None,
            'llm_reasoning': self.llm_reasoning,
            'tags_json': self.tags_json,
            'analysis_type': self.analysis_type,
            'status': self.status,
            'error_message': self.error_message,
            'analyzed_at': self.analyzed_at.isoformat() if self.analyzed_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
