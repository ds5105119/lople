from abc import ABC, abstractmethod
import requests
from fastapi import HTTPException, status


class BaseSocialAuthService(ABC):
    """
    Abstract Base Class for Social Authentication Services.
    """
    @property
    @abstractmethod
    def token_url(self) -> str:
        pass

    @property
    @abstractmethod
    def userinfo_url(self) -> str:
        pass

    @property
    @abstractmethod
    def client_id(self) -> str:
        pass

    @property
    @abstractmethod
    def client_secret(self) -> str:
        pass

    @property
    @abstractmethod
    def redirect_uri(self) -> str:
        pass

    def request_access_token(self, authorization_code: str) -> dict:
        """
        Request Access Token
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
                detail=f"Failed to retrieve access token: {response.text}"
            )

        return response.json()

    def request_userinfo(self, access_token: str) -> dict:
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.get(self.userinfo_url, headers=headers)

        if response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to retrieve user info: {response.text}"
            )

        return response.json()