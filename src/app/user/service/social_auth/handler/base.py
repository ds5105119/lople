from abc import ABC, abstractmethod
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from src.app.user.repository.user import UserRepository
from webtool.auth import JWTService


class BaseSocialAuthHandler(ABC):
    """
    Abstract base handler for social authentication.
    """

    @abstractmethod
    async def handle_callback(
        self,
        session: AsyncSession,
        authorization_code: str,
        user_repository: UserRepository,
        jwt_service: JWTService,
    ) -> dict:
        """
        Handle the social login callback process.
        """
        pass