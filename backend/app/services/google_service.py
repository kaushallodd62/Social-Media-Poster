import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from app.models.oauth_credentials import OAuthCredentials
from app.extensions import db
from app.config import Config
import secrets
from datetime import datetime, timedelta

class GoogleService:
    def __init__(self):
        self.client_id = Config.GOOGLE_CLIENT_ID
        self.client_secret = Config.GOOGLE_CLIENT_SECRET
        self.redirect_uri = Config.GOOGLE_REDIRECT_URI
        # Define all required scopes upfront
        self.required_scopes = [
            'openid',
            'https://www.googleapis.com/auth/userinfo.email',
            'https://www.googleapis.com/auth/userinfo.profile',
            'https://www.googleapis.com/auth/photoslibrary.readonly'
        ]

    def get_auth_url(self, access_type='offline', include_granted_scopes='false'):
        """Get Google OAuth URL"""
        print("Generating Google OAuth URL")
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
            
            print("Created flow object")
            print(f"Using redirect URI: {self.redirect_uri}")
            print(f"Using scopes: {self.required_scopes}")
            
            # Generate state parameter
            state = secrets.token_urlsafe(32)
            
            auth_url, _ = flow.authorization_url(
                access_type=access_type,
                include_granted_scopes=include_granted_scopes,
                state=state
            )
            
            print(f"Generated auth URL: {auth_url}")
            return auth_url, state
        except Exception as e:
            print(f"Error generating auth URL: {str(e)}")
            print(f"Error type: {type(e)}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
            raise

    def get_tokens(self, code):
        """Exchange authorization code for tokens"""
        print("Exchanging authorization code for tokens")
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
            
            print("Created flow object")
            print(f"Using redirect URI: {self.redirect_uri}")
            print(f"Using scopes: {self.required_scopes}")
            
            tokens = flow.fetch_token(
                code=code,
                client_id=self.client_id,
                client_secret=self.client_secret
            )
            
            print(f"Got tokens: {tokens}")
            print(f"Access token: {tokens['access_token'][:10]}...")
            print(f"Refresh token: {tokens.get('refresh_token', 'None')[:10] if tokens.get('refresh_token') else 'None'}...")
            print(f"Expires in: {tokens.get('expires_in')}")
            print(f"Scopes: {tokens.get('scope', '').split()}")
            
            return tokens
        except Exception as e:
            print(f"Error getting tokens: {str(e)}")
            print(f"Error type: {type(e)}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
            raise

    def get_user_info(self, access_token):
        """Get user info from Google"""
        service = build('oauth2', 'v2', credentials=Credentials(access_token))
        return service.userinfo().get().execute()

    def store_credentials(self, user_id, provider, tokens):
        """Store OAuth credentials in database"""
        print(f"Storing credentials for user {user_id}, provider {provider}")
        print(f"Tokens: {tokens}")
        
        credentials = OAuthCredentials.query.filter_by(
            user_id=user_id,
            provider=provider
        ).first()

        if not credentials:
            print("Creating new credentials record")
            credentials = OAuthCredentials(
                user_id=user_id,
                provider=provider
            )

        credentials.access_token = tokens['access_token']
        credentials.refresh_token = tokens.get('refresh_token')
        credentials.token_type = tokens.get('token_type', 'Bearer')
        
        # Convert expires_in (seconds) to datetime
        if 'expires_in' in tokens:
            credentials.token_expires_at = datetime.utcnow() + timedelta(seconds=tokens['expires_in'])
        
        credentials.set_scopes(tokens.get('scopes', []))
        
        print(f"Stored scopes: {credentials.scope}")
        print(f"Stored access token: {credentials.access_token[:10]}...")
        print(f"Stored refresh token: {credentials.refresh_token[:10] if credentials.refresh_token else 'None'}...")
        print(f"Stored token expires at: {credentials.token_expires_at}")
        
        try:
            db.session.add(credentials)
            db.session.commit()
            print("Successfully stored credentials")
        except Exception as e:
            print(f"Error storing credentials: {str(e)}")
            print(f"Error type: {type(e)}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
            db.session.rollback()
            raise

    def get_credentials(self, user_id, provider):
        """Get stored OAuth credentials"""
        print(f"Getting credentials for user {user_id}, provider {provider}")
        
        credentials = OAuthCredentials.query.filter_by(
            user_id=user_id,
            provider=provider
        ).first()

        if not credentials:
            print("No credentials found")
            return None

        print(f"Found credentials with scopes: {credentials.scope}")
        print(f"Access token: {credentials.access_token[:10]}...")
        print(f"Refresh token: {credentials.refresh_token[:10] if credentials.refresh_token else 'None'}...")
        print(f"Token expires at: {credentials.token_expires_at}")
        
        # Create credentials object from stored tokens
        creds = Credentials(
            token=credentials.access_token,
            refresh_token=credentials.refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=self.client_id,
            client_secret=self.client_secret,
            scopes=credentials.scope.split() if credentials.scope else self.required_scopes
        )

        print(f"Created credentials object with scopes: {creds.scopes}")

        # Check if token needs refresh
        if creds.expired and creds.refresh_token:
            print("Token expired, attempting refresh")
            try:
                creds.refresh(Request())
                print("Token refreshed successfully")
                print(f"New access token: {creds.token[:10]}...")
                print(f"New expiry: {creds.expiry}")
                # Update stored credentials
                credentials.access_token = creds.token
                credentials.token_expires_at = creds.expiry
                db.session.commit()
            except Exception as e:
                print(f"Error refreshing token: {str(e)}")
                print(f"Error type: {type(e)}")
                import traceback
                print(f"Traceback: {traceback.format_exc()}")
                # If refresh fails, clear the credentials
                db.session.delete(credentials)
                db.session.commit()
                raise Exception("Failed to refresh token. Please re-authenticate.")

        return creds

    def verify_credentials(self, user_id, provider):
        """Verify that OAuth credentials are valid"""
        print(f"Verifying credentials for user {user_id}, provider {provider}")
        try:
            credentials = self.get_credentials(user_id, provider)
            if not credentials:
                print("No credentials found")
                return False

            print(f"Got credentials with scopes: {credentials.scopes}")
            print(f"Access token: {credentials.token[:10]}...")
            print(f"Refresh token: {credentials.refresh_token[:10] if credentials.refresh_token else 'None'}...")
            print(f"Token expires at: {credentials.expiry}")

            # Check if token needs refresh
            if credentials.expired and credentials.refresh_token:
                print("Token expired, attempting refresh")
                try:
                    credentials.refresh(Request())
                    print("Token refreshed successfully")
                    print(f"New access token: {credentials.token[:10]}...")
                    print(f"New expiry: {credentials.expiry}")
                    # Update stored credentials
                    stored_credentials = OAuthCredentials.query.filter_by(
                        user_id=user_id,
                        provider=provider
                    ).first()
                    if stored_credentials:
                        stored_credentials.access_token = credentials.token
                        stored_credentials.token_expires_at = credentials.expiry
                        db.session.commit()
                        print("Updated stored credentials")
                except Exception as e:
                    print(f"Error refreshing token: {str(e)}")
                    print(f"Error type: {type(e)}")
                    import traceback
                    print(f"Traceback: {traceback.format_exc()}")
                    # If refresh fails, clear the credentials
                    if 'invalid_grant' in str(e).lower():
                        print("Invalid grant error, clearing credentials")
                        self.clear_credentials(user_id, provider)
                        return False
                    raise

            # Test OAuth2 service
            print("Testing OAuth2 service")
            oauth2_service = build('oauth2', 'v2', credentials=credentials)
            user_info = oauth2_service.userinfo().get().execute()
            print(f"Got user info: {user_info}")

            # Test Photos API service
            print("Testing Photos API service")
            photos_service = build('photoslibrary', 'v1', credentials=credentials)
            test_response = photos_service.mediaItems().list(pageSize=1).execute()
            print(f"Got test response: {test_response}")

            return True
        except Exception as e:
            print(f"Error verifying credentials: {str(e)}")
            print(f"Error type: {type(e)}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
            return False

    def clear_credentials(self, user_id, provider):
        """Clear stored OAuth credentials"""
        print(f"Clearing credentials for user {user_id}, provider {provider}")
        
        credentials = OAuthCredentials.query.filter_by(
            user_id=user_id,
            provider=provider
        ).first()

        if credentials:
            print(f"Found credentials with scopes: {credentials.scope}")
            print(f"Access token: {credentials.access_token[:10]}...")
            print(f"Refresh token: {credentials.refresh_token[:10] if credentials.refresh_token else 'None'}...")
            print(f"Token expires at: {credentials.token_expires_at}")
            
            # Clear stored credentials
            credentials.access_token = None
            credentials.refresh_token = None
            credentials.token_expires_at = None
            credentials.scope = None
            
            print("Cleared stored credentials")
            
            try:
                db.session.add(credentials)
                db.session.commit()
                print("Successfully cleared credentials")
            except Exception as e:
                print(f"Error clearing credentials: {str(e)}")
                print(f"Error type: {type(e)}")
                import traceback
                print(f"Traceback: {traceback.format_exc()}")
                db.session.rollback()
                raise 