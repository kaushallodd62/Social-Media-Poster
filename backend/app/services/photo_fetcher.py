import os
import json
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from app.extensions import db
from app.models import OAuthCredentials
from app.config import Config
from app.services.google_service import GoogleService

GOOGLE_PHOTOS_SCOPES = [
    'https://www.googleapis.com/auth/photoslibrary.readonly'
]

def authenticate(user_id):
    """
    Authenticate with Google Photos API using OAuth 2.0 credentials.
    
    Args:
        user_id: The ID of the user to authenticate for
        
    Returns:
        googleapiclient.discovery.Resource: Google Photos API service instance
        
    Raises:
        Exception: If no valid credentials are found and user needs to authenticate
    """
    google_service = GoogleService()
    creds = google_service.get_credentials(user_id, 'google_photos')

    if not creds:
        # This should be handled by the OAuth callback route
        raise Exception("No valid credentials found. Please authenticate through the web interface.")

    try:
        service = build(
            'photoslibrary',
            'v1',
            credentials=creds,
            static_discovery=False
        )
        return service
    except Exception as e:
        print(f"Error building service: {str(e)}")
        print("Please make sure you have enabled the Google Photos Library API in your Google Cloud Console")
        raise

def fetch_media_items(service, page_size=50):
    """
    Fetches media items from Google Photos API.
    
    Args:
        service: Google Photos API service instance
        page_size (int): Number of items to fetch per page
        
    Returns:
        list: List of media items sorted by creation time (newest first)
    """
    response = service.mediaItems().list(pageSize=page_size).execute()
    items = response.get('mediaItems', [])

    # Sort by creationTime descending
    items.sort(key=lambda x: x['mediaMetadata']['creationTime'], reverse=True)

    return items
