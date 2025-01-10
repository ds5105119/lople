from typing import Annotated, Optional

from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPBearer, OAuth2AuthorizationCodeBearer, OAuth2PasswordBearer
from webtool.auth import AuthData


class ExtendOAuth2PasswordBearer(OAuth2PasswordBearer):
    """
    Webtool 인증 미들웨어를 사용하는 Fastapi.security.OAuth2PasswordBearer
    """

    async def __call__(self, request: Request) -> Optional[str]:
        auth = request.scope.get("auth")
        return auth


class ExtendOAuth2AuthorizationCodeBearer(OAuth2AuthorizationCodeBearer):
    """
    Webtool 인증 미들웨어를 사용하는 Fastapi.security.OAuth2AuthorizationCodeBearer
    """

    async def __call__(self, request: Request) -> Optional[str]:
        auth = request.scope.get("auth")
        return auth


class ExtendHTTPBearer(HTTPBearer):
    async def __call__(self, request: Request) -> Optional[str]:
        auth = request.scope.get("auth")
        return auth


oauth_password_schema = ExtendOAuth2PasswordBearer(tokenUrl="/api/user/login")
oauth_authcode_schema = ExtendOAuth2AuthorizationCodeBearer(
    tokenUrl="/api/user/token",
    authorizationUrl="/api/user/authorize",
)
http_bearer = ExtendHTTPBearer()

google_oauth_schema = ExtendOAuth2AuthorizationCodeBearer(
    tokenUrl="https://oauth2.googleapis.com/token",
    authorizationUrl="https://accounts.google.com/o/oauth2/v2/auth",
)

async def get_current_user(
    auth_data: Annotated[AuthData, Depends(http_bearer, use_cache=False)],
) -> AuthData:
    if not auth_data:
        raise HTTPException(status_code=403)

    return auth_data


async def get_current_user_without_error(
    auth_data: Annotated[AuthData, Depends(http_bearer, use_cache=False)],
) -> AuthData:
    return auth_data
