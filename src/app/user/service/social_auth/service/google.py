from fastapi import HTTPException, status
import requests

from src.app.user.service.social_auth.service.base import BaseSocialAuthService
from src.core.dependencies.oauth import google_oauth_schema
from src.core.config import settings



class GoogleAuthService(BaseSocialAuthService):
    token_url = google_oauth_schema.tokenUrl
    userinfo_url = "https://www.googleapis.com/oauth2/v2/userinfo"
    client_id = settings.google.client_id
    client_secret = settings.google.secret_key
    redirect_uri = settings.google.redirect_uri

    def request_access_token(self, authorization_code: str) -> dict:
        """
        Request access token from Google OAuth server
        """
        data = {
            "grant_type": "authorization_code",
            "code": authorization_code,
            "redirect_uri": self.redirect_uri,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
        }
        response = requests.post(self.token_url, data=data)
        if response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to retrieve Google access token"
            )
        return response.json()

    def request_userinfo(self, access_token: str) -> dict:
        """
        Request user information from Google API
        """
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.get(self.userinfo_url, headers=headers)
        if response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to retrieve user info"
            )
        return response.json()