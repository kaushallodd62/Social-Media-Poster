from flask import Flask, render_template, jsonify
from photo_fetcher import authenticate, fetch_media_items
from llm_ranking_service import LLMBasedRankingService
from datetime import datetime
import requests

app = Flask(__name__)

# Initialize Google Photos service
service = None
ranking = LLMBasedRankingService()

def get_photo_service():
    global service
    if service is None:
        service = authenticate()
    return service

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/photos')
def get_photos():
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

@app.route('/api/rank/<photo_id>')
def rank_photo(photo_id):
    try:
        # Find the photo in our current photos list
        service = get_photo_service()
        photo = service.mediaItems().get(mediaItemId=photo_id).execute()
        
        if not photo:
            return jsonify({'success': False, 'error': 'Photo not found'})

        # Prepare the photo data for ranking
        photo_data = {
            'id': photo['id'],
            'description': photo.get('description', ''),
            'filename': photo['filename'],
            'baseUrl': photo['baseUrl'],
            'mediaMetadata': photo['mediaMetadata'],
        }

        # Get the scores
        scores = ranking.rate_image(photo_data)
        
        return jsonify({
            'success': True,
            'scores': scores,
            'overall': scores.get('overall', 0.0)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/photo/<photo_id>')
def get_photo(photo_id):
    try:
        service = get_photo_service()
        photo = service.mediaItems().get(mediaItemId=photo_id).execute()
        return jsonify({'success': True, 'photo': photo})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True) 
