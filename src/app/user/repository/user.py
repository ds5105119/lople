from typing import Sequence

from sqlalchemy import or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.sql import exists
from sqlalchemy.sql.base import ExecutableOption
from webtool.auth import AuthData

from src.app.user.model.user import Profile, User
from src.core.models.repository import (
    ABaseCreateRepository,
    ABaseDeleteRepository,
    ABaseReadRepository,
    ABaseUpdateRepository,
)


class UserCreateRepository(ABaseCreateRepository[User]):
    pass


class UserReadRepository(ABaseReadRepository[User]):
    async def is_exist(self, session: AsyncSession, email: str | None = None, username: str | None = None):
        if email is None and username is None:
            raise ValueError("Either 'email' or 'username' must be provided")
        filters = [
            f
            for f in (
                self.model.email == email if email else None,
                self.model.username == username if username else None,
            )
            if f is not None
        ]
        result = await self.get(
            session,
            stmt=[exists().where(or_(*filters))],
        )
        return result

    async def get_user_by_email(self, session: AsyncSession, email: str):
        result = await self.get_instance(
            session,
            filters=[self.model.email == email],
            options=[selectinload(self.model.profile)],
        )
        return result

    async def get_user_by_handle(self, session: AsyncSession, username: str):
        result = await self.get_instance(
            session,
            filters=[self.model.username == username],
            options=[selectinload(self.model.profile)],
        )
        return result

    async def get_user_by_auth_data(
        self,
        session: AsyncSession,
        auth_data: AuthData,
        options: Sequence[ExecutableOption] = None,
    ) -> User | None:
        """
        Args:
            session: Annotated 된 AsyncSession Generator
            auth_data: webtool.AuthData
            options: sqlalchemy.sql.base.ExecutableOption

        Returns: User | None
        """
        options = [selectinload(self.model.profile)] if options is None else options
        user = await self.get_instance(
            session,
            filters=[self.model.id == int(auth_data.identifier)],
            options=options,
        )

        return user.scalar()


class UserUpdateRepository(ABaseUpdateRepository[User]):
    pass


class UserDeleteRepository(ABaseDeleteRepository[User]):
    pass


class UserRepository(
    UserCreateRepository,
    UserReadRepository,
    UserUpdateRepository,
    UserDeleteRepository,
):
    pass


class ProfileCreateRepository(ABaseCreateRepository[Profile]):
    pass


class ProfileReadRepository(ABaseReadRepository[Profile]):
    pass


class ProfileUpdateRepository(ABaseUpdateRepository[Profile]):
    pass


class ProfileDeleteRepository(ABaseDeleteRepository[Profile]):
    pass


class ProfileRepository(
    ProfileCreateRepository,
    ProfileReadRepository,
    ProfileUpdateRepository,
    ProfileDeleteRepository,
):
    pass
