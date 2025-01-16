from abc import ABC, abstractmethod
from typing import Union, Tuple, Any


class SocialAuthBase(ABC):
    """
    소셜 로그인 공통 기능을 정의한 추상 클래스(API 통합 설계 기본 틀)
    """

    @abstractmethod
    async def get_access_token(self, auth_code: str) -> str:
        """
        OAuth2 인증 코드로 Access Token을 반환
        Args:
            auth_code: 소셜 플랫폼에서 전달받은 인증 코드

        Returns:
            소셜 플랫폼에서 발급된 Access Token
        """
        pass

    @abstractmethod
    async def get_user_info(self, access_token: str) -> Union[dict, Any]:
        """
        Access Token으로 사용자 정보를 가져옴
        Args:
            access_token: 소셜 플랫폼에서 발급된 Access Token

        Returns:
            소셜 사용자 정보 (플랫폼별 데이터는 표준화하여 반환)
        """
        pass
