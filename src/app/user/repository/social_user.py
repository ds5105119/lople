from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from src.app.user.model.user import User
from src.app.user.schema.social_user import SocialUserVerificationDTO
from src.core.models.repository import (
    ABaseReadRepository,
    ABaseCreateRepository,
    ABaseUpdateRepository
)


class SocialUserReadRepository(ABaseReadRepository[User]):

    async def get_user(
            self,
            session: AsyncSession,
            data: SocialUserVerificationDTO,
    ) -> Optional[User]:
        """
        Retrieve a user based on email, social_id, and social_provider.

        Args:
            session: The database session.
            data: The social_auth user verification data.

        Returns:
            User or None: The user object if found, else None.
        """
        filters = [self.model.email == data.email]

        if data.social_provider:  # 소셜 사용자
            filters.extend([
                self.model.social_id == data.social_id,
                self.model.social_provider == data.social_provider,
                self.model.user_type == "social"
            ])
        else:  # 일반 사용자
            filters.extend([
                self.model.social_id.is_(None),
                self.model.social_provider.is_(None),
                self.model.user_type == "general"
            ])

        user = await self.get_instance(
            session=session,
            filters=filters,
        )

        return user.scalar()

class SocialUserCreateRepository(ABaseCreateRepository[User]):
    """
    Repository for creating social_auth users
    """
    pass

class SocialUserUpdateRepository(ABaseUpdateRepository[User]):
    """
    Repository for updating social_auth user data
    """
    pass


class SocialUserRepository(
    SocialUserReadRepository,
    SocialUserCreateRepository,
    SocialUserUpdateRepository
):
    pass
