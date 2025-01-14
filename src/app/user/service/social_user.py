from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.user.service.social_auth.google import GoogleAuth
from src.app.user.schema.social_user import SocialUserRegisterDTO as SocialUser


class SocialAuthService:
    pass