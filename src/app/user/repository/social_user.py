from sqlalchemy.ext.asyncio import AsyncSession
from src.app.user.model.user import User
from src.app.user.schema.social_user import SocialUserVerificationDTO
from src.core.models.repository import (
    ABaseReadRepository,
    ABaseCreateRepository,
    ABaseUpdateRepository
)


class SocialUserReadRepository(ABaseReadRepository[User]):
    """
    Repository specialized in retrieving social_auth users
    """

    async def get_user(
            self,
            session: AsyncSession,
            data: SocialUserVerificationDTO,
    ) -> tuple[User | None, str]:
        """
        Retrieve a user based on email and social_auth provider.

        Args:
            session: The database session.
            data: The social_auth user verification data.

        Returns:
            tuple: A tuple of (User, status).
                   status:
                   - "general" if user is a general user (social_provider is None).
                   - "social_auth" if user is a social_auth user.
                   - "not_found" if no user matches.
        """
        filters = []
        status = "not_found"

        if data.email and data.social_provider:
            # Add both email and social_provider to filters
            filters.append(self.model.email == data.email)
            filters.append(self.model.social_provider == data.social_provider)
        elif data.email:
            # Fallback to just email if social_provider is not provided
            filters.append(self.model.email == data.email)

        # Retrieve user using combined filters
        user = await self.get_instance(
            session=session,
            filters=filters,
        )

        user_instance = user.scalar()
        if user_instance:
            if user_instance.social_provider:
                status = "social_auth"
            else:
                status = "general"

        return user_instance, status

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
