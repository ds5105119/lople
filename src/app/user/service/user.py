from typing import cast

import argon2
from fastapi import Depends, HTTPException, Request, Response, status
from webtool.auth import JWTService

from src.app.user.model.user import User
from src.app.user.repository.user import ProfileRepository, UserRepository
from src.app.user.schema.user import (
    LoginDto,
    LoginResponse,
    LoginResponseUser,
    PartialProfileDto,
    RegisterDto,
    TokenDto,
)
from src.core.dependencies.db import postgres_session
from src.core.dependencies.oauth import get_current_user


class UserService:
    def __init__(
        self,
        user_repository: UserRepository,
        profile_repository: ProfileRepository,
        jwt_service: JWTService,
        refresh_token_name: str = "refresh",
    ):
        self.user_repository = user_repository
        self.profile_repository = profile_repository
        self.jwt_service = jwt_service
        self.password_hasher = argon2.PasswordHasher()
        self.refresh_token_name = refresh_token_name

    @staticmethod
    def _user_to_claim(user):
        return {"sub": str(user.id)}

    def _get_refresh_token(self, request: Request):
        """
        Args:
            request: Starlette Request

        Returns:
            refresh token

        Raises:
            HTTPException

        """
        refresh = request.cookies.get(self.refresh_token_name)
        if refresh:
            return refresh
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials provided.",
        )

    async def _generate_tokens(self, user: User) -> tuple[str, str]:
        """
        토큰 생성

        Args:
            user: db 내 User 스칼라. PK 필수

        Returns:
            access, refresh 토큰 (Webtool)
        """
        payload = self._user_to_claim(user)
        return await self.jwt_service.create_token(payload)

    async def _generate_refresh(self, refresh: str) -> tuple[str, str]:
        """
        토큰 재발급

        Args:
            refresh: 기존 발급된 refresh token

        Returns:
            access, refresh 토큰 (Webtool)
        """
        refresh_data = await self.jwt_service.validate_refresh_token(refresh)
        return await self.jwt_service.update_token(refresh_data, refresh)

    async def _generate_login_response(self, response: Response, user: User) -> LoginResponse:
        """
        로그인 응답 생성

        Args:
            response: Fastapi.Response
            user: db 내 User 스칼라. PK 필수

        Returns:
            LoginResponse
        """
        access, refresh = await self._generate_tokens(user)
        response.set_cookie(key=self.refresh_token_name, value=refresh, httponly=True, secure=True)

        return LoginResponse(access=access, user=LoginResponseUser.model_validate(user))

    async def _generate_refresh_response(self, response: Response, refresh: str) -> TokenDto:
        """
        토큰 재발급 응답 생성

        Args:
            response: Fastapi.Response
            refresh: 기존 refresh token

        Returns:
            새롭게 발급된 access, refresh tokens
        """
        access, refresh = await self._generate_refresh(refresh)
        response.set_cookie(key=self.refresh_token_name, value=refresh, httponly=True, secure=True)

        return TokenDto(access=access)

    async def _validate_registration(self, data: RegisterDto, session: postgres_session) -> User:
        """
        회원가입 유효성 검사

        Args:
            data: register.RegisterDto
            session: Session

        Returns:
            읽은 유저 데이터

        Raises:
            HTTPException: 이메일 또는 username 가 Table 에서 Unique 하지 않은 경우 409 에러 반환
        """
        user = await self.user_repository.get_unique_fields(session, cast(str, data.email), data.username)

        if user.all():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"email {data.email} already exists",
            )

        return user

    def _validate_password(self, hashed_password: str, password: str) -> None:
        """
        패스워드 유효성 검사

        Args:
            hashed_password: 해시된 암호
            password: 입력된 암호

        Returns:
            None

        Raises:
            HTTPException: 암호가 올바르지 않은 경우 401 에러 반환
        """
        try:
            self.password_hasher.verify(hashed_password, password)
        except (argon2.exceptions.Argon2Error, AttributeError, ValueError):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials provided.",
            )

    async def _validate_login(self, data: LoginDto, session: postgres_session):
        """
        로그인 유효성 검사

        Args:
            data: LoginDto
            session: Session

        Returns:
            읽은 유저 데이터

        Raises:
            HTTPException: 유저를 찾을 수 없는 경우 401 에러 반환
        """
        if data.email:
            user = await self.user_repository.get_user_by_email(session, cast(str, data.email))
        else:
            user = await self.user_repository.get_user_by_handle(session, data.username)

        user_data = user.scalar()
        if not user_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials provided.",
            )

        self._validate_password(user_data.password, data.password)
        return user_data

    async def register_user(self, data: RegisterDto, session: postgres_session, response: Response) -> LoginResponse:
        user = await self._validate_registration(data, session)
        data = data.model_dump(by_alias=True)
        data["password"] = self.password_hasher.hash(data["password"])

        user = await self.user_repository.create(session, **data)
        await session.refresh(user, attribute_names=["profile"])
        return await self._generate_login_response(response, user)

    async def login_user(self, data: LoginDto, session: postgres_session, response: Response) -> LoginResponse:
        user = await self._validate_login(data, session)
        return await self._generate_login_response(response, user)

    async def logout_user(
        self,
        request: Request,
        response: Response,
    ) -> None:
        refresh = self._get_refresh_token(request)
        response.delete_cookie(key=self.refresh_token_name, httponly=True, secure=True)
        await self.jwt_service.invalidate_token(refresh)

    async def refresh_tokens(
        self,
        request: Request,
        response: Response,
    ) -> TokenDto:
        refresh = self._get_refresh_token(request)
        return await self._generate_refresh_response(response, refresh)

    async def update_profile(
        self,
        data: PartialProfileDto,
        session: postgres_session,
        auth_data=Depends(get_current_user),
    ):
        data = data.model_dump()
        await self.profile_repository.update(
            session,
            filters=[self.profile_repository.model.user_id == int(auth_data.identifier)],
            **data,
        )

    async def delete_user(self, session: postgres_session, auth_data=Depends(get_current_user)):
        await self.user_repository.update(
            session,
            filters=[self.user_repository.model.id == int(auth_data.identifier)],
            is_deleted=True,
        )

    async def inactive_user(self, session: postgres_session, auth_data=Depends(get_current_user)):
        await self.user_repository.update(
            session,
            filters=[self.user_repository.model.id == int(auth_data.identifier)],
            is_active=False,
        )
