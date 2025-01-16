import httpx
from typing import Optional
from fastapi import HTTPException, Response


from src.app.user.service.social_auth.base import SocialAuthBase
from src.app.user.service.user import UserService
from src.core.config import settings
from src.app.user.schema.user import PartialProfileDto
from src.app.user.schema.social_user import (
    SocialUserVerificationDTO,
    SocialUserInfoResponse,
    SocialProvider,
    UserType,
    SocialUserRegisterDTO
)
from src.app.user.repository.social_user import SocialUserRepository
from src.app.user.model.user import User
from src.core.utils.social_api.data_helper import get_value
from src.core.dependencies.db import postgres_session



class GoogleOAuthService(SocialAuthBase):

    def __init__(self, social_user_repository: SocialUserRepository):
        self.client_id = settings.oauth_google.client_id
        self.client_secret = settings.oauth_google.secret_key
        self.redirect_uri = settings.oauth_google.redirect_uri
        self.token_url = settings.oauth_google.token_url
        self.people_api_url = settings.oauth_google.people_api_url
        self.user_info_url = settings.oauth_google.user_info_url
        self.social_user_repository = social_user_repository
        self.http_client = httpx.AsyncClient()


    async def get_access_token(self, code: str) -> str:
        payload = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "redirect_uri": self.redirect_uri,
            "code": code,
            "grant_type": "authorization_code",
        }
        async with self.http_client as client:
            response = await client.post(self.token_url, data=payload)
            response.raise_for_status()
            return response.json()["access_token"]

    async def fetch_user_info_api(self, access_token: str) -> dict:
        headers = {"Authorization": f"Bearer {access_token}"}
        async with self.http_client as client:
            response = await client.get(self.user_info_url, headers=headers)
            response.raise_for_status()
            return response.json()

    async def fetch_people_api(self, access_token: str) -> dict:
        headers = {"Authorization": f"Bearer {access_token}"}
        async with self.http_client as client:
            response = await client.get(
                self.people_api_url,
                headers=headers,
                params={"personFields": "genders,birthdays"}  # 필요한 데이터만 요청
            )
            response.raise_for_status()
            return response.json()

    async def get_user_info(self, code: str) -> SocialUserInfoResponse:
        """
        Google User Info API와 People API에서 사용자 데이터를 가져옵니다.

        Args:
            code: Google OAuth Authorization 코드.

        Returns:
            dict: 구조화된 사용자 데이터.
        """
        access_token = await self.get_access_token(code)
        user_info = await self.fetch_user_info_api(access_token)
        people_data = await self.fetch_people_api(access_token)

        social_id = user_info.get("sub")
        email = user_info.get("email")
        username = user_info.get("name")

        if not all([social_id, email, username]):
            raise HTTPException(
                status_code=400,
                detail="Missing required user information from User Info API."
            )

        gender = get_value("genders", "value", people_data)
        birthday = get_value("birthdays", "date", people_data, is_date=True)

        profile = PartialProfileDto(
            sex=gender,
            birthday=birthday,
            profile="",
            bio="",
            link="",
        ) if gender or birthday else None

        return SocialUserInfoResponse(
            social_id=social_id,
            email=email,
            username=username,
            profile=profile
        )

    async def _validate_user_info(self, session: postgres_session, data: SocialUserInfoResponse) -> Optional[User]:
        """
        사용자 정보를 유효성 검사

        Args:
            session.
            data: 사용자 정보 (SocialUserInfoResponse).
            social_provider: 소셜 제공자 (e.g., google, kakao).

        Returns:
            User or None: 유효한 소셜 사용자 객체가 있다면 반환, 없으면 None.

        Raises:
            HTTPException: 일반 사용자 중복, 소셜 사용자 중복 등 에러 상황 처리.
        """
        # 중복 계정 확인
        existing_user = await self.social_user_repository.get_user(
            session=session,
            data=SocialUserVerificationDTO(
                email=data.email,
                social_id=data.social_id,
                social_provider=SocialProvider.google,
                user_type=UserType.social
            )
        )

        if existing_user:
            if existing_user.user_type == UserType.general:
                raise HTTPException(
                    status_code=409,
                    detail="An account with this email already exists as a general user."
                )
            elif (
                    existing_user.user_type == UserType.social
                    and existing_user.social_provider == SocialProvider.google
                    and existing_user.social_id == data.social_id
            ):
                # 동일한 소셜 사용자
                return existing_user

            # 동일 이메일로 다른 소셜 계정이 존재하는 경우
            raise HTTPException(
                status_code=409,
                detail="An account with this email is already registered with a different social login."
            )

        # 검증 완료, 새 사용자로 등록 가능
        return None

    async def register_social_user(self, session: postgres_session, data: SocialUserInfoResponse) -> User:
        """
        새 사용자 등록을 수행
        """
        return await self.social_user_repository.create(
            session=session,
            instance_data={
                "email": data.email,
                "username": data.username,
                "social_provider": data.social_provider,
                "social_id": data.social_id,
                "profile": data.profile.dict() if data.profile else {},
            }
        )

    async def handle_google_auth(self, session: postgres_session, code: str, response: Response,user_service: UserService):
        """
        Google OAuth 인증 및 JWT 응답 생성

        Args:
            session: 데이터베이스 세션
            code: Google OAuth 인증 코드
            response: FastAPI Response 객체 (쿠키 설정 용도)
            user_service: UserService 객체 (JWT 생성 및 로그인 응답 생성)
        Returns:
            LoginResponse: 사용자 정보와 JWT access_token 포함된 응답 반환

        Note: 로그인 로직 미완성
        """
        # Get google user info
        user_info = await self.get_user_info(code)

        # Validate user
        user = await self._validate_user_info(session, user_info)

        if user:
            # Process login for existing social user
            return await user_service._generate_login_response(response, user)

        # Register new social user with issue jwt
        social_user = await self.register_social_user(session, user_info)
        return await user_service._generate_login_response(response, social_user)

