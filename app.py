from flask import Flask, render_template, jsonify
from photo_fetcher import authenticate, fetch_media_items
from ranking_service import RankingService
from datetime import datetime
from io import BytesIO
from PIL import Image
import requests

app = Flask(__name__)

# Initialize Google Photos service
service = None
ranking = RankingService()

def load_image(url: str) -> Image.Image | None:
    """Fetch an image from ``url`` and return a PIL Image."""
    try:
        resp = requests.get(url)
        resp.raise_for_status()
        return Image.open(BytesIO(resp.content))
    except Exception:
        return None

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
        favorites = fetch_media_items(service, favorites_only=True, page_size=30)
        recent = fetch_media_items(service, favorites_only=False, page_size=50)

        combined = favorites + [item for item in recent if item not in favorites]

        items = []
        for photo in combined[:20]:  # Limit to 20 photos for now
            is_fav = photo in favorites
            metadata = {
                'creation_time': datetime.fromisoformat(
                    photo['mediaMetadata']['creationTime'].replace('Z', '+00:00')
                ),
                'is_favorite': is_fav,
            }
            img = load_image(photo['baseUrl'] + '=w256-h256')
            items.append({'image': img, 'metadata': metadata, 'photo': photo})

        ranked = ranking.rank_images(items)

        photos = []
        for item in ranked:
            photo = item['photo']
            score_details = {k: round(v, 4) for k, v in item['scores'].items()}
            photos.append({
                'id': photo['id'],
                'filename': photo['filename'],
                'creationTime': photo['mediaMetadata']['creationTime'],
                'mimeType': photo['mimeType'],
                'baseUrl': photo['baseUrl'],
                'isFavorite': item['metadata']['is_favorite'],
                'score': round(item['total_score'], 4),
                'scores': score_details,
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
