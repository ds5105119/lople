from abc import ABC, abstractmethod
from typing import Optional


class SocialAuthBase(ABC):
    """
    소셜 로그인 공통 기능을 정의한 추상 클래스(API 통합 설계 기본 틀)
    """

    def __init__(self, client_id: str, client_secret: str, redirect_uri: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri

    @abstractmethod
    async def get_access_token(self, code: str) -> str:
        """
        OAuth2 인증 코드로 Access Token을 반환
        Args:
            code: 소셜 플랫폼에서 전달받은 인증 코드

        Returns:
            소셜 플랫폼에서 발급된 Access Token
        """
        pass

    @abstractmethod
    async def get_user_info(self, access_token: str) -> dict:
        """
        Access Token으로 사용자 정보를 가져옴
        Args:
            access_token: 소셜 플랫폼에서 발급된 Access Token

        Returns:
            소셜 사용자 정보 (플랫폼별 데이터는 표준화하여 반환)
        """
        pass

    async def logout(self, access_token: str) -> bool:
        """
        (선택적 구현) Access Token으로 소셜 세션 무효화
        Args:
            access_token: 소셜 플랫폼에서 발급된 Access Token

        Returns:
            로그아웃 성공 여부
        """
        return True
