from flask import Blueprint, jsonify, request, redirect, url_for
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta
from sqlalchemy import desc
import json

from app.extensions import db
from app.models import User, OAuthCredentials, MediaItem, RankingSession, MediaRanking
from app.services.photo_fetcher import authenticate, fetch_media_items
from app.services.llm_ranking_service import LLMBasedRankingService
from app.config import Config

# Initialize services
photo_service = None
ranking_service = LLMBasedRankingService()

routes_bp = Blueprint('routes', __name__)

def get_photo_service():
    """Get or initialize the photo service."""
    global photo_service
    if photo_service is None:
        photo_service = authenticate()
    return photo_service

def register_routes(app):
    """Register all API routes with the Flask application."""
    
    @routes_bp.route('/api/health')
    def health_check():
        """Health check endpoint."""
        return jsonify({"status": "healthy"})

    @routes_bp.route('/api/photos')
    def get_photos():
        """Get list of photos from Google Photos."""
        try:
            service = get_photo_service()
            items = []
            for mediaItem in fetch_media_items(service, page_size=50):
                items.append({
                    'id': mediaItem['id'],
                    'description': mediaItem.get('description', ''),
                    'filename': mediaItem['filename'],
                    'baseUrl': mediaItem['baseUrl'],
                    'mediaMetadata': mediaItem['mediaMetadata'],
                })
            return jsonify({'success': True, 'photos': items})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})

    @routes_bp.route('/api/photo/<photo_id>')
    def get_photo(photo_id):
        try:
            service = get_photo_service()
            photo = service.mediaItems().get(mediaItemId=photo_id).execute()
            return jsonify({'success': True, 'photo': photo})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})

    @routes_bp.route('/api/photos/top-picks')
    def get_top_picks():
        # For MVP, hardcode user_id=1
        user_id = 1
        
        # Find the latest completed ranking session
        latest_session = RankingSession.query.filter(
            RankingSession.user_id == user_id,
            RankingSession.completed_at.isnot(None)
        ).order_by(desc(RankingSession.completed_at)).first()
        
        if not latest_session:
            return jsonify({'photos': []})
        
        # Get top 20 photos from the latest session
        top_rankings = MediaRanking.query.filter_by(
            ranking_session_id=latest_session.id
        ).order_by(desc(MediaRanking.combined_score)).limit(20).all()
        
        # Join with MediaItem to get photo details
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

    @routes_bp.route('/api/photos/sync', methods=['POST'])
    def sync_photos():
        # For MVP, hardcode user_id=1
        user_id = 1
        
        try:
            service = get_photo_service()
            items = fetch_media_items(service, page_size=50)
            
            for mediaItem in items:
                # Check if item already exists
                existing = MediaItem.query.filter_by(
                    user_id=user_id,
                    google_media_id=mediaItem['id']
                ).first()
                
                if existing:
                    # Update existing item
                    existing.base_url = mediaItem['baseUrl']
                    existing.filename = mediaItem.get('filename')
                    existing.mime_type = mediaItem.get('mimeType')
                    existing.creation_time = datetime.fromisoformat(mediaItem['mediaMetadata']['creationTime'].replace('Z', '+00:00'))
                    existing.width = mediaItem['mediaMetadata'].get('width')
                    existing.height = mediaItem['mediaMetadata'].get('height')
                    existing.last_synced_at = datetime.utcnow()
                else:
                    # Create new item
                    new_item = MediaItem(
                        user_id=user_id,
                        google_media_id=mediaItem['id'],
                        base_url=mediaItem['baseUrl'],
                        filename=mediaItem.get('filename'),
                        mime_type=mediaItem.get('mimeType'),
                        creation_time=datetime.fromisoformat(mediaItem['mediaMetadata']['creationTime'].replace('Z', '+00:00')),
                        width=mediaItem['mediaMetadata'].get('width'),
                        height=mediaItem['mediaMetadata'].get('height')
                    )
                    db.session.add(new_item)
            
            db.session.commit()
            return jsonify({'success': True, 'message': 'Photos synced successfully'})
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'error': str(e)}), 500

    @routes_bp.route('/api/photos/rank', methods=['POST'])
    def rank_photos():
        # For MVP, hardcode user_id=1
        user_id = 1
        
        try:
            # Create a new ranking session
            session = RankingSession(
                user_id=user_id,
                method='ai_ranking'
            )
            db.session.add(session)
            db.session.flush()  # Get session.id
            
            # Get all non-deleted photos
            photos = MediaItem.query.filter_by(
                user_id=user_id,
                is_deleted=False
            ).all()
            
            # Rank each photo
            for photo in photos:
                # Get photo data from Google Photos
                service = get_photo_service()
                google_photo = service.mediaItems().get(mediaItemId=photo.google_media_id).execute()
                
                # Prepare photo data for ranking
                photo_data = {
                    'id': google_photo['id'],
                    'description': google_photo.get('description', ''),
                    'filename': google_photo['filename'],
                    'baseUrl': google_photo['baseUrl'],
                    'mediaMetadata': google_photo['mediaMetadata'],
                }
                
                # Get scores from ranking service
                scores = ranking_service.rate_image(photo_data)
                
                # Create ranking
                ranking = MediaRanking(
                    ranking_session_id=session.id,
                    media_item_id=photo.id,
                    technical_score=scores.get('technical', 0.0),
                    aesthetic_score=scores.get('aesthetic', 0.0),
                    combined_score=scores.get('overall', 0.0),
                    llm_reasoning=scores.get('reasoning'),
                    tags_json=scores.get('tags', [])
                )
                db.session.add(ranking)
            
            # Mark session as completed
            session.completed_at = datetime.utcnow()
            db.session.commit()
            
            return jsonify({'success': True, 'message': 'Photos ranked successfully'})
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'error': str(e)}), 500

    @routes_bp.route('/api/photos/disconnect', methods=['POST'])
    def disconnect_photos():
        """Disconnect from Google Photos by removing OAuth credentials."""
        try:
            # For MVP, hardcode user_id=1
            user_id = 1
            
            # Find and delete the OAuth credentials
            oauth_cred = OAuthCredentials.query.filter_by(
                user_id=user_id,
                provider='google_photos'
            ).first()
            
            if oauth_cred:
                db.session.delete(oauth_cred)
                db.session.commit()
                return jsonify({'success': True, 'message': 'Successfully disconnected from Google Photos'})
            else:
                return jsonify({'success': False, 'error': 'No Google Photos connection found'}), 404
                
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'error': str(e)}), 500

    @routes_bp.route('/api/photos/connection-status')
    def check_photos_connection():
        try:
            service = get_photo_service()
            # Make a minimal API call to verify credentials
            service.mediaItems().list(pageSize=1).execute()
            return jsonify({'success': True, 'connected': True})
        except Exception as e:
            return jsonify({'success': False, 'connected': False, 'error': str(e)})

    @routes_bp.route('/api/media/items', methods=['GET'])
    @jwt_required()
    def get_media_items():
        """Get all media items for the current user"""
        try:
            user_id = get_jwt_identity()
            items = MediaItem.query.filter_by(user_id=user_id).all()
            return jsonify([item.to_dict() for item in items])
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @routes_bp.route('/api/media/items/<int:item_id>', methods=['GET'])
    @jwt_required()
    def get_media_item(item_id):
        """Get a specific media item"""
        try:
            user_id = get_jwt_identity()
            item = MediaItem.query.filter_by(id=item_id, user_id=user_id).first()
            if not item:
                return jsonify({'error': 'Media item not found'}), 404
            return jsonify(item.to_dict())
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @routes_bp.route('/api/media/items', methods=['POST'])
    @jwt_required()
    def create_media_item():
        """Create a new media item"""
        try:
            user_id = get_jwt_identity()
            data = request.get_json()
            
            if not data or not data.get('url'):
                return jsonify({'error': 'URL is required'}), 400
            
            item = MediaItem(
                user_id=user_id,
                url=data['url'],
                title=data.get('title', ''),
                description=data.get('description', ''),
                media_type=data.get('media_type', 'image')
            )
            
            db.session.add(item)
            db.session.commit()
            
            return jsonify(item.to_dict()), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500

    @routes_bp.route('/api/media/items/<int:item_id>', methods=['PUT'])
    @jwt_required()
    def update_media_item(item_id):
        """Update a media item"""
        try:
            user_id = get_jwt_identity()
            item = MediaItem.query.filter_by(id=item_id, user_id=user_id).first()
            
            if not item:
                return jsonify({'error': 'Media item not found'}), 404
            
            data = request.get_json()
            
            if data.get('title'):
                item.title = data['title']
            if data.get('description'):
                item.description = data['description']
            if data.get('url'):
                item.url = data['url']
            if data.get('media_type'):
                item.media_type = data['media_type']
            
            db.session.commit()
            
            return jsonify(item.to_dict())
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500

    @routes_bp.route('/api/media/items/<int:item_id>', methods=['DELETE'])
    @jwt_required()
    def delete_media_item(item_id):
        """Delete a media item"""
        try:
            user_id = get_jwt_identity()
            item = MediaItem.query.filter_by(id=item_id, user_id=user_id).first()
            
            if not item:
                return jsonify({'error': 'Media item not found'}), 404
            
            db.session.delete(item)
            db.session.commit()
            
            return jsonify({'message': 'Media item deleted successfully'})
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500

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