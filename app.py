from flask import Flask, render_template, jsonify, request
from photo_fetcher import authenticate, fetch_media_items
import os
from PIL import Image
import io
import base64
from datetime import datetime

app = Flask(__name__)

# Initialize Google Photos service
service = None

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
        # Fetch both favorites and recent photos
        favorites = fetch_media_items(service, favorites_only=True, page_size=30)
        recent = fetch_media_items(service, favorites_only=False, page_size=50)
        
        # Combine and deduplicate photos
        combined = favorites + [item for item in recent if item not in favorites]
        
        # Format the response
        photos = []
        for photo in combined[:20]:  # Limit to 20 photos for now
            photos.append({
                'id': photo['id'],
                'filename': photo['filename'],
                'creationTime': photo['mediaMetadata']['creationTime'],
                'mimeType': photo['mimeType'],
                'baseUrl': photo['baseUrl'],
                'isFavorite': photo in favorites
            })
        
        return jsonify({'success': True, 'photos': photos})
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