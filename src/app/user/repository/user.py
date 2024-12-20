from sqlalchemy import or_
from sqlalchemy.ext.asyncio import AsyncSession as Session

from src.app.user.model.user import User
from src.core.models.repository import (
    ABaseCreateRepository,
    ABaseDeleteRepository,
    ABaseReadRepository,
    ABaseUpdateRepository,
)


class UserCreateRepository(ABaseCreateRepository[User]):
    pass


class UserReadRepository(ABaseReadRepository[User]):
    async def get_unique_fields(self, session: Session, email: str, handle: str):
        result = await self.get(
            session,
            columns=["email", "handle"],
            filters=[
                or_(
                    self.model.email == email,
                    self.model.handle == handle,
                ),
            ],
        )
        return result

    async def get_user_by_email(self, session: Session, email: str):
        result = await self.get(session, columns=["id", "password"], filters=[self.model.email == email])
        return result

    async def get_user_by_handle(self, session: Session, handle: str):
        result = await self.get(session, columns=["id", "password"], filters=[self.model.handle == handle])
        return result


class UserUpdateRepository(ABaseUpdateRepository[User]):
    pass


class UserDeleteRepository(ABaseDeleteRepository[User]):
    pass


class UserRepository(UserCreateRepository, UserReadRepository, UserUpdateRepository, UserDeleteRepository):
    pass
