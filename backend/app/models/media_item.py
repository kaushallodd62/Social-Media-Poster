from app.extensions import db
from sqlalchemy.dialects.postgresql import JSONB, ARRAY
from datetime import datetime
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

class MediaItem(db.Model):
    """
    SQLAlchemy model for a media item (photo) belonging to a user.
    """
    __tablename__ = "media_items"
    
    id = db.Column(db.BigInteger, primary_key=True)
    user_id = db.Column(db.BigInteger, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    google_media_id = db.Column(db.String(255), nullable=False)
    base_url = db.Column(db.Text, nullable=False)
    filename = db.Column(db.String(255))
    mime_type = db.Column(db.String(50))
    description = db.Column(db.Text)  # From Google Photos
    creation_time = db.Column(db.DateTime(timezone=True))
    width = db.Column(db.Integer)
    height = db.Column(db.Integer)
    is_deleted = db.Column(db.Boolean, nullable=False, default=False)
    last_synced_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now())
    exif_json = db.Column(JSONB)  # For storing EXIF data
    tags_json = db.Column(ARRAY(db.Text))
    created_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now())
    updated_at = db.Column(db.DateTime(timezone=True), server_default=db.func.now(), onupdate=db.func.now())
    duration = db.Column(db.Integer, nullable=True)  # Duration in seconds for videos
    thumbnail_url = db.Column(db.Text, nullable=True)  # Thumbnail for UI
    ai_status = db.Column(db.String(20), default='pending')  # 'pending', 'analyzed', etc.
    latest_ranking_id = db.Column(db.BigInteger, db.ForeignKey('media_rankings.id'), nullable=True)

    __table_args__ = (
        db.UniqueConstraint("user_id", "google_media_id", name="uq_user_media"),
    )

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert media item to dictionary.
        Returns:
            dict: Dictionary representation of the media item.
        """
        return {
            'id': self.id,
            'user_id': self.user_id,
            'google_media_id': self.google_media_id,
            'base_url': self.base_url,
            'filename': self.filename,
            'mime_type': self.mime_type,
            'description': self.description,
            'creation_time': self.creation_time.isoformat() if self.creation_time else None,
            'width': self.width,
            'height': self.height,
            'duration': self.duration,
            'thumbnail_url': self.thumbnail_url,
            'is_deleted': self.is_deleted,
            'last_synced_at': self.last_synced_at.isoformat() if self.last_synced_at else None,
            'exif_json': self.exif_json,
            'tags_json': self.tags_json,
            'ai_status': self.ai_status,
            'latest_ranking_id': self.latest_ranking_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
