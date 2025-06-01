import os
import json
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from app.extensions import db
from app.models import OAuthCredentials
from app.config import Config

# If modifying these scopes, update the GOOGLE_AUTH_SCOPES in .env
SCOPES = [Config.GOOGLE_AUTH_SCOPES]

def authenticate(user_id):
    """
    Authenticate with Google Photos API using OAuth 2.0 credentials from environment variables.
    
    Args:
        user_id: The ID of the user to authenticate for
        
    Returns:
        googleapiclient.discovery.Resource: Google Photos API service instance
        
    Raises:
        Exception: If no valid credentials are found and user needs to authenticate
    """
    creds = None
    
    oauth_cred = OAuthCredentials.query.filter_by(
        provider='google_photos',
        user_id=user_id
    ).first()

    if oauth_cred:
        creds = Credentials(
            token=oauth_cred.access_token,
            refresh_token=oauth_cred.refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=Config.GOOGLE_CLIENT_ID,
            client_secret=Config.GOOGLE_CLIENT_SECRET,
            scopes=SCOPES
        )

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            # Update stored credentials
            if oauth_cred:
                oauth_cred.access_token = creds.token
                oauth_cred.token_expires_at = creds.expiry
                db.session.commit()
        else:
            # Create OAuth 2.0 flow
            flow = Flow.from_client_config(
                {
                    "web": {
                        "client_id": Config.GOOGLE_CLIENT_ID,
                        "client_secret": Config.GOOGLE_CLIENT_SECRET,
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token",
                        "redirect_uris": [Config.GOOGLE_REDIRECT_URI]
                    }
                },
                scopes=SCOPES
            )
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
