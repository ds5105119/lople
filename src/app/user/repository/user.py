from sqlalchemy import or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

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
    async def get_unique_fields(self, session: AsyncSession, email: str, username: str):
        result = await self.get(
            session,
            columns=[self.model.email, self.model.username],
            filters=[
                or_(
                    self.model.email == email,
                    self.model.username == username,
                ),
            ],
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
