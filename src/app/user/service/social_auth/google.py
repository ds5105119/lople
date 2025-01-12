from fastapi import HTTPException
from src.app.user.service.social_auth.base import BaseSocialAuthService
from src.core.config import settings
from src.app.user.model.user import User
from src.app.user.service.user import UserService
from src.core.dependencies.db import postgres_session


class GoogleAuthService(BaseSocialAuthService):
    def __init__(self):
        super().__init__(config=settings.google)
        self.UserService = UserService

    async def authenticate_user(self, authorization_code: str) -> User:
        # 1. Request Access Token via Authorization Code
        token_response = self.request_access_token(authorization_code=authorization_code)
        access_token = token_response.get("access_token")
        if not access_token:
            raise HTTPException(status_code=400, detail="Failed to retrieve Google access token")

        # 2. Reqeust UserInfo via Access Token
        user_info = self.request_userinfo(access_token=access_token)
        google_user_id = user_info.get("id")  # Google 기본 사용자 ID
        email = user_info.get("email")
        name = user_info.get("name")

        if not google_user_id or not email:
            raise HTTPException(status_code=400, detail="Invalid user info retrieved from Google.")

        # 3. Check userinfo via user's email
        existing_user = await self.UserService._get_user_by_email(session=postgres_session, email=email)
        if not existing_user:
            # Register new user
            new_user = User(
                email=email,
                username=name,  # 구글에서 받아온 이름 사용
                google_id=google_user_id,  # Google ID 추가 필드
            )
            await self.UserService.register_user(new_user, session=postgres_session)  # 등록
            return new_user

        # 기존 사용자 반환
        return existing_user
