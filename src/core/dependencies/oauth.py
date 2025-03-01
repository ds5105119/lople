from typing import Annotated, Optional

from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPBearer


class ExtendHTTPBearer(HTTPBearer):
    async def __call__(self, request: Request) -> Optional[str]:
        auth = request.scope.get("auth")
        return auth


http_bearer = ExtendHTTPBearer()


async def get_current_user(
    data: Annotated[dict, Depends(http_bearer, use_cache=False)],
) -> dict:
    if not data:
        raise HTTPException(status_code=403)

    return data


async def get_current_user_without_error(
    data: Annotated[dict, Depends(http_bearer, use_cache=False)],
) -> dict:
    return data or {}
