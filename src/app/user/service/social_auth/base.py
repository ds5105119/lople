from abc import ABC, abstractmethod
import requests
from fastapi import HTTPException, status
from src.core.config import settings, SocialOauth


class BaseSocialAuthService(ABC):
    def __init__(self, config: SocialOauth):
        self.config = config

    def handle_response(self, response: requests.Response, error_message: str) -> dict:
        if response.status_code != 200:
            try:
                error_data = response.json()
                error_detail = error_data.get("error_description", error_data.get("error", "Unknown error"))
            except ValueError:
                error_detail = response.text

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"{error_message}: {error_detail}"
            )

        return response.json()

    def request_access_token(self, authorization_code: str) -> dict:
        data = {
            "grant_type": "authorization_code",
            "code": authorization_code,
            "redirect_uri": self.config.redirect_uri,
            "client_id": self.config.client_id,
            "client_secret": self.config.client_secret,
        }
        response = requests.post(self.config.token_url, data=data)
        response_data = self.handle_response(response, "Failed to retrieve access token")

        if "access_token" not in response_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Access token is missing in the response"
            )

        return response_data

    def request_userinfo(self, access_token: str) -> dict:
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.get(self.config.userinfo_url, headers=headers)
        response_data = self.handle_response(response, "Failed to retrieve user info")

        if "id" not in response_data or "email" not in response_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User info is missing mandatory fields"
            )

        return response_data