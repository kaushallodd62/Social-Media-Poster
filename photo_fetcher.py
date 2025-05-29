import os
import json
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/photoslibrary.readonly']
TOKEN_PATH = 'token.json'
CREDS_PATH = 'credentials.json'

def authenticate():
    creds = None

    # Load saved user credentials
    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)

    # If no valid creds, run the OAuth flow
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDS_PATH, SCOPES)
            creds = flow.run_local_server(port=0)
        # Save for next time
        with open(TOKEN_PATH, 'w') as token_file:
            token_file.write(creds.to_json())

    try:
        # Build the Photos service (with discovery cache disabled)
        service = build(
            'photoslibrary',
            'v1',
            credentials=creds,
            cache_discovery=False,
            static_discovery=False
        )
        return service
    except Exception as e:
        print(f"Error building service: {str(e)}")
        print("Please make sure you have enabled the Google Photos Library API in your Google Cloud Console")
        raise


def fetch_media_items(service, favorites_only=False, page_size=50):
    """
    Fetches media items. If ``favorites_only`` is ``True`` the returned list only
    contains items that have the ``isFavorite`` flag set. Otherwise the latest
    ``page_size`` items are returned sorted by reverse ``creationTime``.
    """
    response = service.mediaItems().list(pageSize=page_size).execute()
    items = response.get('mediaItems', [])

    # Sort by creationTime descending
    items.sort(key=lambda x: x['mediaMetadata']['creationTime'], reverse=True)

    if favorites_only:
        items = [item for item in items if item.get('isFavorite')]

    return items


if __name__ == '__main__':
    service = authenticate()
    # Fetch top 30 favorites first, then fill with recent if needed
    favorites = fetch_media_items(service, favorites_only=True, page_size=30)
    recent = fetch_media_items(service, favorites_only=False, page_size=50)

    # Combine, giving weight to favorites
    combined = favorites + [item for item in recent if item not in favorites]

    for idx, media in enumerate(combined[:20], start=1):
        print(f"{idx}. {media['filename']} ({media['mediaMetadata']['creationTime']}) - ID: {media['id']}")
