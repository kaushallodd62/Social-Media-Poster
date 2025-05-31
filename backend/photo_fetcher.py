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
    """
    Authenticate with Google Photos API. 
    """
    creds = None

    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDS_PATH, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_PATH, 'w') as token_file:
            token_file.write(creds.to_json())

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
    Fetches media items. The latest ``page_size`` items are returned sorted by reverse ``creationTime``.
    """
    response = service.mediaItems().list(pageSize=page_size).execute()
    items = response.get('mediaItems', [])

    # Sort by creationTime descending
    items.sort(key=lambda x: x['mediaMetadata']['creationTime'], reverse=True)

    return items
