from sqlalchemy.ext.asyncio import AsyncSession
from src.app.user.model.user import User
from src.core.models.repository import (
    ABaseReadRepository,
    ABaseCreateRepository,
    ABaseUpdateRepository
)


class SocialUserReadRepository(ABaseReadRepository[User]):
    """
    Repository specialized in retrieving social users
    """

    async def get_user(self, session: AsyncSession,
                       email: str | None = None,
                       social_provider: str | None = None,
                       social_id: str | None = None
                       ) -> User | None:
        """
        Retrieve a user based on email or social data.

        Args:
            session: The database session.
            email: The user's email to search with.
            social_provider: The social provider (e.g., "google").
            social_id: The social ID linked to the provider.

        Returns:
            User | None: The matched user or None if no user is found.
        """
        filters = []

        if email:
            filters.append(self.model.email == email)
        if social_provider and social_id:
            filters.append(self.model.social_provider == social_provider)
            filters.append(self.model.social_id == social_id)

        # Retrieve user using combined filters
        user = await self.get_instance(
            session,
            filters=filters,
        )
        return user.scalar()


class SocialUserCreateRepository(ABaseCreateRepository[User]):
    """
    Repository for creating social users
    """
    pass

class SocialUserUpdateRepository(ABaseUpdateRepository[User]):
    """
    Repository for updating social user data
    """
    pass


class SocialUserRepository(
    SocialUserReadRepository,
    SocialUserCreateRepository,
    SocialUserUpdateRepository
):
    pass
