import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from app.models.oauth_credentials import OAuthCredentials
from app.extensions import db
from app.config import Config

class GoogleService:
    def __init__(self):
        self.client_id = Config.GOOGLE_CLIENT_ID
        self.client_secret = Config.GOOGLE_CLIENT_SECRET
        self.redirect_uri = Config.GOOGLE_REDIRECT_URI

    def get_auth_url(self, scopes=None, access_type='offline', include_granted_scopes='true'):
        """Get Google OAuth URL"""
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                }
            },
            scopes=scopes,
            redirect_uri=self.redirect_uri
        )
        
        return flow.authorization_url(
            access_type=access_type,
            include_granted_scopes=include_granted_scopes
        )[0]

    def get_tokens(self, auth_code, scopes=None):
        """Exchange authorization code for tokens"""
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                }
            },
            scopes=scopes,
            redirect_uri=self.redirect_uri
        )
        
        flow.fetch_token(code=auth_code)
        return {
            'access_token': flow.credentials.token,
            'refresh_token': flow.credentials.refresh_token,
            'token_type': 'Bearer', # Google always returns Bearer
            'expires_in': flow.credentials.expiry.timestamp() if flow.credentials.expiry else None
        }

    def get_user_info(self, access_token):
        """Get user info from Google"""
        service = build('oauth2', 'v2', credentials=Credentials(access_token))
        return service.userinfo().get().execute()

    def store_credentials(self, user_id, provider, tokens):
        """Store OAuth credentials in database"""
        credentials = OAuthCredentials.query.filter_by(
            user_id=user_id,
            provider=provider
        ).first()

        if not credentials:
            credentials = OAuthCredentials(
                user_id=user_id,
                provider=provider
            )

        credentials.access_token = tokens['access_token']
        credentials.refresh_token = tokens.get('refresh_token')
        credentials.token_type = tokens.get('token_type', 'Bearer')
        credentials.token_expires_at = tokens.get('expires_in')
        
        db.session.add(credentials)
        db.session.commit()

    def get_credentials(self, user_id, provider):
        """Get stored OAuth credentials"""
        credentials = OAuthCredentials.query.filter_by(
            user_id=user_id,
            provider=provider
        ).first()

        if not credentials:
            return None

        # Check if token needs refresh
        if credentials.token_expires_at and credentials.refresh_token:
            creds = Credentials(
                token=credentials.access_token,
                refresh_token=credentials.refresh_token,
                token_uri="https://oauth2.googleapis.com/token",
                client_id=self.client_id,
                client_secret=self.client_secret,
                scopes=credentials.scopes
            )

            if creds.expired:
                creds.refresh(Request())
                self.store_credentials(user_id, provider, {
                    'access_token': creds.token,
                    'refresh_token': creds.refresh_token,
                    'token_type': 'Bearer',
                    'expires_in': creds.expiry.timestamp() if creds.expiry else None
                })
                return creds

        return Credentials(
            token=credentials.access_token,
            refresh_token=credentials.refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=self.client_id,
            client_secret=self.client_secret,
            scopes=credentials.scopes
        ) 