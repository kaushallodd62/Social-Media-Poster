from flask import Blueprint, jsonify, request, redirect, url_for
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta
from sqlalchemy import desc
import json
from googleapiclient.discovery import build
from typing import Any
import logging

from app.extensions import db
from app.models import User, OAuthCredentials, MediaItem, RankingSession, MediaRanking
from app.services.google_service import GoogleService
from app.services.llm_ranking_service import LLMBasedRankingService
from app.config import Config

# Initialize services
ranking_service = LLMBasedRankingService()

routes_bp = Blueprint('routes', __name__)

logger = logging.getLogger(__name__)

# Health check endpoint
@routes_bp.route('/api/health')
def health_check() -> Any:
    """
    Health check endpoint.
    Returns:
        JSON response with status.
    """
    return jsonify({"status": "healthy"})

# --- Media endpoints (Picker-based) ---
@routes_bp.route('/api/media/items', methods=['GET'])
@jwt_required()
def get_media_items() -> Any:
    """
    Get all media items for the current user.
    Returns:
        JSON response with all media items or error.
    """
    try:
        user_id = get_jwt_identity()
        items = MediaItem.query.filter_by(user_id=user_id).all()
        logger.info(f"Fetched {len(items)} media items for user_id={user_id}")
        return jsonify([item.to_dict() for item in items])
    except Exception as e:
        logger.error(f"Failed to get media items: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@routes_bp.route('/api/media/items/<int:item_id>', methods=['GET'])
@jwt_required()
def get_media_item(item_id: int) -> Any:
    """
    Get a specific media item by ID for the current user.
    Args:
        item_id (int): The media item ID.
    Returns:
        JSON response with the media item or error.
    """
    try:
        user_id = get_jwt_identity()
        item = MediaItem.query.filter_by(id=item_id, user_id=user_id).first()
        if not item:
            logger.warning(f"Media item {item_id} not found for user_id={user_id}")
            return jsonify({'error': 'Media item not found'}), 404
        logger.info(f"Fetched media item {item_id} for user_id={user_id}")
        return jsonify(item.to_dict())
    except Exception as e:
        logger.error(f"Failed to get media item {item_id}: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@routes_bp.route('/api/media/items', methods=['POST'])
@jwt_required()
def create_media_item() -> Any:
    """
    Create a new media item for the current user.
    Returns:
        JSON response with the created media item or error.
    """
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        if not data or not data.get('base_url') or not data.get('google_media_id'):
            logger.warning(f"Missing base_url or google_media_id in create_media_item for user_id={user_id}")
            return jsonify({'error': 'base_url and google_media_id are required'}), 400
        item = MediaItem(
            user_id=user_id,
            base_url=data['base_url'],
            google_media_id=data['google_media_id'],
            filename=data.get('filename'),
            mime_type=data.get('mime_type'),
            description=data.get('description', ''),
            creation_time=None,
            width=data.get('width'),
            height=data.get('height')
        )
        db.session.add(item)
        db.session.commit()
        logger.info(f"Created media item {item.id} for user_id={user_id}")
        return jsonify(item.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        logger.error(f"Failed to create media item: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@routes_bp.route('/api/media/items/<int:item_id>', methods=['PUT'])
@jwt_required()
def update_media_item(item_id: int) -> Any:
    """
    Update a media item for the current user.
    Args:
        item_id (int): The media item ID.
    Returns:
        JSON response with the updated media item or error.
    """
    try:
        user_id = get_jwt_identity()
        item = MediaItem.query.filter_by(id=item_id, user_id=user_id).first()
        if not item:
            logger.warning(f"Media item {item_id} not found for user_id={user_id}")
            return jsonify({'error': 'Media item not found'}), 404
        data = request.get_json()
        if data.get('title'):
            item.title = data['title']
        if data.get('description'):
            item.description = data['description']
        if data.get('base_url'):
            item.base_url = data['base_url']
        if data.get('google_media_id'):
            item.google_media_id = data['google_media_id']
        if data.get('filename'):
            item.filename = data['filename']
        db.session.commit()
        logger.info(f"Updated media item {item_id} for user_id={user_id}")
        return jsonify(item.to_dict())
    except Exception as e:
        db.session.rollback()
        logger.error(f"Failed to update media item {item_id}: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@routes_bp.route('/api/media/items/<int:item_id>', methods=['DELETE'])
@jwt_required()
def delete_media_item(item_id: int) -> Any:
    """
    Delete a media item for the current user.
    Args:
        item_id (int): The media item ID.
    Returns:
        JSON response with success or error message.
    """
    try:
        user_id = get_jwt_identity()
        item = MediaItem.query.filter_by(id=item_id, user_id=user_id).first()
        if not item:
            logger.warning(f"Media item {item_id} not found for user_id={user_id}")
            return jsonify({'error': 'Media item not found'}), 404
        db.session.delete(item)
        db.session.commit()
        logger.info(f"Deleted media item {item_id} for user_id={user_id}")
        return jsonify({'message': 'Media item deleted successfully'})
    except Exception as e:
        db.session.rollback()
        logger.error(f"Failed to delete media item {item_id}: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500

@routes_bp.route('/api/photos/top-picks')
@jwt_required()
def get_top_picks() -> Any:
    """
    Get top 20 photos from the latest completed ranking session for the current user.
    Returns:
        JSON response with top photos.
    """
    user_id = get_jwt_identity()
    latest_session = RankingSession.query.filter(
        RankingSession.user_id == user_id,
        RankingSession.completed_at.isnot(None)
    ).order_by(desc(RankingSession.completed_at)).first()
    if not latest_session:
        return jsonify({'photos': []})
    top_rankings = MediaRanking.query.filter_by(
        ranking_session_id=latest_session.id
    ).order_by(desc(MediaRanking.combined_score)).limit(20).all()
    results = []
    for ranking in top_rankings:
        media_item = db.session.get(MediaItem, ranking.media_item_id)
        if media_item and not media_item.is_deleted:
            results.append({
                'google_media_id': media_item.google_media_id,
                'base_url': media_item.base_url,
                'combined_score': float(ranking.combined_score),
                'tags': ranking.tags_json or [],
                'width': media_item.width,
                'height': media_item.height
            })
    return jsonify({'photos': results})

@routes_bp.route('/api/ranking/sessions', methods=['GET'])
@jwt_required()
def get_ranking_sessions():
    """Get all ranking sessions for the current user"""
    try:
        user_id = get_jwt_identity()
        sessions = RankingSession.query.filter_by(user_id=user_id).all()
        return jsonify([session.to_dict() for session in sessions])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@routes_bp.route('/api/ranking/sessions/<int:session_id>', methods=['GET'])
@jwt_required()
def get_ranking_session(session_id):
    """Get a specific ranking session"""
    try:
        user_id = get_jwt_identity()
        session = RankingSession.query.filter_by(
            id=session_id, user_id=user_id
        ).first()
        
        if not session:
            return jsonify({'error': 'Ranking session not found'}), 404
        
        return jsonify(session.to_dict())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@routes_bp.route('/api/ranking/sessions', methods=['POST'])
@jwt_required()
def create_ranking_session():
    """Create a new ranking session"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data or not data.get('media_items'):
            return jsonify({'error': 'Media items are required'}), 400
        
        session = RankingSession(
            user_id=user_id,
            name=data.get('name', 'New Ranking Session'),
            description=data.get('description', '')
        )
        
        db.session.add(session)
        db.session.flush()
        
        # Create media rankings for each item
        for item_data in data['media_items']:
            ranking = MediaRanking(
                session_id=session.id,
                media_item_id=item_data['id'],
                initial_rank=item_data.get('initial_rank', 0)
            )
            db.session.add(ranking)
        
        db.session.commit()
        
        return jsonify(session.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@routes_bp.route('/api/ranking/sessions/<int:session_id>/rank', methods=['POST'])
@jwt_required()
def rank_media_items(session_id):
    """Rank media items in a session using LLM"""
    try:
        user_id = get_jwt_identity()
        session = RankingSession.query.filter_by(
            id=session_id, user_id=user_id
        ).first()
        
        if not session:
            return jsonify({'error': 'Ranking session not found'}), 404
        
        # Get all media items in the session
        rankings = MediaRanking.query.filter_by(session_id=session.id).all()
        media_items = [ranking.media_item for ranking in rankings]
        
        # Get rankings from LLM service
        ranked_items = ranking_service.rank_media_items(media_items)
        
        # Update rankings in database
        for item, rank in ranked_items:
            ranking = MediaRanking.query.filter_by(
                session_id=session.id,
                media_item_id=item.id
            ).first()
            ranking.final_rank = rank
        
        db.session.commit()
        
        return jsonify(session.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@routes_bp.route('/api/media/items/batch', methods=['POST'])
@jwt_required()
def batch_create_media_items() -> Any:
    """
    Batch create or update media items for the current user.
    Accepts a list of media item metadata from the frontend (Google Photos Picker).
    Returns:
        JSON response with the stored media items (with DB IDs) or error.
    """
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        if not isinstance(data, list):
            return jsonify({'error': 'Request body must be a list of media items'}), 400
        stored_items = []
        for item in data:
            google_media_id = item.get('google_media_id') or item.get('id')
            base_url = item.get('base_url') or item.get('baseUrl')
            if not google_media_id or not base_url:
                logger.warning(f"Missing google_media_id or base_url in item: {item}")
                continue
            # Check if item already exists for this user
            existing = MediaItem.query.filter_by(user_id=user_id, google_media_id=google_media_id).first()
            if existing:
                # Update fields if changed
                existing.base_url = base_url
                existing.filename = item.get('filename')
                existing.mime_type = item.get('mime_type') or item.get('mimeType')
                existing.description = item.get('description', '')
                existing.creation_time = item.get('creation_time') or item.get('creationTime')
                existing.width = item.get('width')
                existing.height = item.get('height')
                existing.duration = item.get('duration')
                existing.thumbnail_url = item.get('thumbnail_url') or item.get('thumbnailUrl')
                existing.last_synced_at = datetime.utcnow()
                logger.info(f"Updated media item {existing.id} for user_id={user_id}")
                db.session.add(existing)
                stored_items.append(existing)
            else:
                new_item = MediaItem(
                    user_id=user_id,
                    google_media_id=google_media_id,
                    base_url=base_url,
                    filename=item.get('filename'),
                    mime_type=item.get('mime_type') or item.get('mimeType'),
                    description=item.get('description', ''),
                    creation_time=item.get('creation_time') or item.get('creationTime'),
                    width=item.get('width'),
                    height=item.get('height'),
                    duration=item.get('duration'),
                    thumbnail_url=item.get('thumbnail_url') or item.get('thumbnailUrl'),
                )
                db.session.add(new_item)
                stored_items.append(new_item)
        db.session.commit()
        return jsonify([item.to_dict() for item in stored_items]), 201
    except Exception as e:
        db.session.rollback()
        logger.error(f"Failed to batch create media items: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500 