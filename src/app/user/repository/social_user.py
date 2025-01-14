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

    async def get_user(
            self,
            session: AsyncSession,
            email: str | None = None,
            social_provider: str | None = None,
    ) -> tuple[User | None, str]:
        """
        Retrieve a user based on email and social provider.

        Args:
            session: The database session.
            email: The user's email to search with.
            social_provider: The social provider (e.g., "google").

        Returns:
            tuple: A tuple of (User, status).
                   status:
                   - "general" if user is a general user (social_provider is None).
                   - "social" if user is a social user.
                   - "not_found" if no user matches.
        """
        filters = []
        status = "not_found"

        if email and social_provider:
            # Add both email and social_provider to filters
            filters.append(self.model.email == email)
            filters.append(self.model.social_provider == social_provider)
        elif email:
            # Fallback to just email if social_provider is not provided
            filters.append(self.model.email == email)

        # Retrieve user using combined filters
        user = await self.get_instance(
            session=session,
            filters=filters,
        )

        user_instance = user.scalar()
        if user_instance:
            if user_instance.social_provider:
                status = "social"
            else:
                status = "general"

        return user_instance, status

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
