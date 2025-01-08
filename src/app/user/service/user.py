from typing import cast

import argon2
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import selectinload
from webtool.auth import JWTService

from src.app.user.model.user import User
from src.app.user.repository.user import ProfileRepository, UserRepository
from src.app.user.schema.user import LoginDto, PartialProfileDto, RegisterDto
from src.core.dependencies.db import postgres_session
from src.core.dependencies.oauth import get_current_user


class UserService:
    def __init__(self, user_repository: UserRepository, profile_repository: ProfileRepository, jwt_service: JWTService):
        self.user_repository = user_repository
        self.profile_repository = profile_repository
        self.jwt_service = jwt_service
        self.password_hasher = argon2.PasswordHasher()

    @staticmethod
    def _user_to_claim(user):
        return {
            "sub": str(user.id),
        }

    async def _get_user(self, session: postgres_session, auth_data) -> User:
        user_data = await self.user_repository.get_instance(
            session,
            [self.user_repository.model.id == int(auth_data.identifier)],
            options=[selectinload(self.user_repository.model.profile)],
        )

        return user_data.scalar()

    async def _issue_tokens(self, db_user):
        """
        Parameters:
            db_user: 유저 데이터. PK 필수

        Returns: access, refresh 토큰 (Webtool)
        """
        payload = self._user_to_claim(db_user)
        return await self.jwt_service.create_token(payload)

    async def _is_register_valid(self, data: RegisterDto, session: postgres_session):
        """
        Parameters:
            data: register.RegisterDto
            session: Session

        Returns: 읽은 유저 데이터
        """
        user = await self.user_repository.get_unique_fields(session, cast(str, data.email), data.username)

        if user.all():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"email {data.email} already exists",
            )

        return user

    async def _is_login_valid(self, data: LoginDto, session: postgres_session):
        """
        Parameters:
            data: login.LoginDto
            session: Session

        Returns: 읽은 유저 데이터
        """
        if data.email:
            user = await self.user_repository.get_user_by_email(session, cast(str, data.email))
        else:
            user = await self.user_repository.get_user_by_handle(session, data.username)

        user = user.mappings().first()

        try:
            self.password_hasher.verify(user.password, data.password)
        except (argon2.exceptions.Argon2Error, AttributeError, ValueError):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Can not find user",
            )

        return user

    async def register_user(self, data: RegisterDto, session: postgres_session):
        """
        Parameters:
            data: register.RegisterDto
            session: Session

        Returns:
            tuple: access, refresh 토큰
        """
        user = await self._is_register_valid(data, session)

        data = data.model_dump(by_alias=True)
        data["password"] = self.password_hasher.hash(data["password"])
        user = await self.user_repository.create(session, **data)

        access, refresh = await self._issue_tokens(user)
        return access, refresh

    async def login_user(self, data: LoginDto, session: postgres_session):
        """
        Parameters:
            data: login.LoginDto
            session: Session

        Returns:
            tuple: access, refresh 토큰
        """
        user = await self._is_login_valid(data, session)

        access, refresh = await self._issue_tokens(user)
        return access, refresh

    async def update_profile(
        self,
        data: PartialProfileDto,
        session: postgres_session,
        auth_data=Depends(get_current_user),
    ):
        data = data.model_dump()
        await self.profile_repository.update(
            session, [self.profile_repository.model.user_id == int(auth_data.identifier)], **data
        )

    async def logout_user(self, refresh_token: str):
        await self.jwt_service.invalidate_token(refresh_token)
