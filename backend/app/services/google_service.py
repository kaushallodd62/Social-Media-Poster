import os
import logging
from typing import Optional, List, Dict, Any
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from app.models.oauth_credentials import OAuthCredentials
from app.extensions import db
from app.config import Config
import secrets
from datetime import datetime, timedelta
import requests

logger = logging.getLogger(__name__)

class GoogleService:
    """
    Service for handling Google OAuth and API interactions, including token management and user info retrieval.
    """
    def __init__(self) -> None:
        """
        Initialize GoogleService with configuration and required scopes.
        """
        self.client_id = Config.GOOGLE_CLIENT_ID
        self.client_secret = Config.GOOGLE_CLIENT_SECRET
        self.redirect_uri = Config.GOOGLE_REDIRECT_URI
        self.required_scopes: List[str] = [
            'openid',
            'https://www.googleapis.com/auth/userinfo.email',
            'https://www.googleapis.com/auth/userinfo.profile',
            'https://www.googleapis.com/auth/photoslibrary.readonly'
        ]

    def get_auth_url(self, access_type: str = 'offline', include_granted_scopes: bool = False) -> str:
        """
        Generate Google OAuth URL for user authentication.

        Args:
            access_type (str): OAuth access type ('offline' or 'online').
            include_granted_scopes (bool): Whether to include previously granted scopes.

        Returns:
            str: The Google OAuth authorization URL.
        """
        try:
            flow = Flow.from_client_config(
                {
                    "web": {
                        "client_id": self.client_id,
                        "client_secret": self.client_secret,
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token",
                    }
                },
                scopes=self.required_scopes,
                redirect_uri=self.redirect_uri
            )
            state = secrets.token_urlsafe(32)
            include_granted_scopes_str = str(include_granted_scopes).lower()
            auth_url, _ = flow.authorization_url(
                access_type=access_type,
                include_granted_scopes=include_granted_scopes_str,
                state=state
            )
            return auth_url
        except Exception as e:
            logger.error(f"Error generating auth URL: {str(e)}", exc_info=True)
            raise

    def get_tokens(self, code: str) -> Dict[str, Any]:
        """
        Exchange authorization code for tokens.

        Args:
            code (str): The authorization code from Google OAuth.

        Returns:
            dict: Token information including access and refresh tokens.
        """
        try:
            flow = Flow.from_client_config(
                {
                    "web": {
                        "client_id": self.client_id,
                        "client_secret": self.client_secret,
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token",
                    }
                },
                scopes=self.required_scopes,
                redirect_uri=self.redirect_uri
            )
            tokens = flow.fetch_token(
                code=code,
                client_id=self.client_id,
                client_secret=self.client_secret
            )
            scopes = tokens.get('scope', [])
            if isinstance(scopes, str):
                scopes = scopes.split()
            # Only log if tokeninfo fetch fails
            tokeninfo_url = f"https://www.googleapis.com/oauth2/v1/tokeninfo?access_token={tokens['access_token']}"
            try:
                requests.get(tokeninfo_url)
            except Exception as e:
                logger.warning(f"Error fetching tokeninfo: {e}")
            return tokens
        except Exception as e:
            logger.error(f"Error getting tokens: {str(e)}", exc_info=True)
            raise

    def get_user_info(self, access_token: str) -> Dict[str, Any]:
        """
        Get user info from Google using an access token.

        Args:
            access_token (str): The Google OAuth access token.

        Returns:
            dict: User information from Google.
        """
        service = build('oauth2', 'v2', credentials=Credentials(access_token))
        return service.userinfo().get().execute()

    def store_credentials(self, user_id: int, provider: str, tokens: Dict[str, Any]) -> None:
        """
        Store OAuth credentials in the database.

        Args:
            user_id (int): The user's ID.
            provider (str): The OAuth provider name.
            tokens (dict): Token information to store.
        """
        credentials = OAuthCredentials.query.filter_by(
            user_id=user_id,
            provider=provider
        ).first()
        if not credentials:
            credentials = OAuthCredentials(
                user_id=user_id,
                provider=provider
            )
            logger.info(f"Created new credentials record for user_id={user_id}, provider={provider}")
        credentials.access_token = tokens['access_token']
        credentials.refresh_token = tokens.get('refresh_token')
        credentials.token_type = tokens.get('token_type', 'Bearer')
        if 'expires_in' in tokens:
            credentials.token_expires_at = datetime.utcnow() + timedelta(seconds=tokens['expires_in'])
        else:
            credentials.token_expires_at = datetime.utcnow() + timedelta(hours=1)
        scopes = tokens.get('scope')
        if scopes:
            if isinstance(scopes, str):
                scopes = scopes.split()
            if not scopes:
                logger.warning("Empty scopes list being passed to set_scopes!")
            credentials.set_scopes(scopes)
        else:
            credentials.set_scopes(self.required_scopes)
        try:
            db.session.add(credentials)
            db.session.commit()
            logger.info(f"Stored/updated credentials for user_id={user_id}, provider={provider}")
        except Exception as e:
            logger.error(f"Error storing credentials: {str(e)}", exc_info=True)
            db.session.rollback()
            raise

    def _get_and_refresh_credentials(self, user_id: int, provider: str) -> Optional[Credentials]:
        """
        Fetch credentials from DB, refresh if expired, update DB, and return Credentials object or None.

        Args:
            user_id (int): The user's ID.
            provider (str): The OAuth provider name.

        Returns:
            Credentials or None: A valid Credentials object, or None if not found or refresh failed.
        """
        credentials = OAuthCredentials.query.filter_by(
            user_id=user_id,
            provider=provider
        ).first()
        if not credentials:
            return None
        creds = Credentials(
            token=credentials.access_token,
            refresh_token=credentials.refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=self.client_id,
            client_secret=self.client_secret,
            scopes=credentials.get_scopes() if credentials.scope else self.required_scopes
        )
        if creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
                credentials.access_token = creds.token
                credentials.token_expires_at = creds.expiry
                db.session.commit()
                logger.info(f"Token refreshed for user_id={user_id}, provider={provider}")
            except Exception as e:
                logger.error(f"Error refreshing token: {str(e)}", exc_info=True)
                logger.warning("Failed to refresh token. Clearing credentials.")
                self.clear_credentials(user_id, provider)
                return None
        return creds

    def get_credentials(self, user_id: int, provider: str) -> Optional[Credentials]:
        """
        Get stored OAuth credentials, refreshing if needed.

        Args:
            user_id (int): The user's ID.
            provider (str): The OAuth provider name.

        Returns:
            Credentials or None: A valid Credentials object, or None if not found or refresh failed.
        """
        return self._get_and_refresh_credentials(user_id, provider)

    def verify_credentials(self, user_id: int, provider: str) -> bool:
        """
        Verify that OAuth credentials are valid by making test API calls.

        Args:
            user_id (int): The user's ID.
            provider (str): The OAuth provider name.

        Returns:
            bool: True if credentials are valid, False otherwise.
        """
        try:
            credentials = self.get_credentials(user_id, provider)
            if not credentials:
                logger.warning("No credentials found or failed to refresh.")
                return False
            oauth2_service = build('oauth2', 'v2', credentials=credentials)
            user_info = oauth2_service.userinfo().get().execute()
            photos_service = build('photoslibrary', 'v1', credentials=credentials)
            test_response = photos_service.mediaItems().list(pageSize=1).execute()
            if not test_response.get('mediaItems'):
                albums_response = photos_service.albums().list(pageSize=5).execute()
            logger.info(f"Successfully verified credentials for user_id={user_id}, provider={provider}")
            return True
        except Exception as e:
            logger.error(f"Error verifying credentials: {str(e)}", exc_info=True)
            return False

    def clear_credentials(self, user_id: int, provider: str) -> None:
        """
        Clear stored OAuth credentials for a user and provider.

        Args:
            user_id (int): The user's ID.
            provider (str): The OAuth provider name.
        """
        credentials = OAuthCredentials.query.filter_by(
            user_id=user_id,
            provider=provider
        ).first()
        if credentials:
            credentials.access_token = None
            credentials.refresh_token = None
            credentials.token_expires_at = None
            credentials.scope = None
            try:
                db.session.add(credentials)
                db.session.commit()
                logger.info(f"Cleared credentials for user_id={user_id}, provider={provider}")
            except Exception as e:
                logger.error(f"Error clearing credentials: {str(e)}", exc_info=True)
                db.session.rollback()
                raise 