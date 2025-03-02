from datetime import date
from typing import Annotated, Optional

from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPBearer
from pydantic import BaseModel, field_validator


class User(BaseModel):
    sub: str
    username: str
    gender: str
    birthdate: str | date

    @field_validator("birthdate", mode="before")
    def parse_birthdate(cls, value):
        return date.fromisoformat(value) if isinstance(value, str) else value


class ExtendHTTPBearer(HTTPBearer):
    async def __call__(self, request: Request) -> Optional[str]:
        auth = request.scope.get("auth")
        return auth


http_bearer = ExtendHTTPBearer()


async def _get_current_user(
    data: Annotated[dict, Depends(http_bearer, use_cache=False)],
) -> User:
    if not data:
        raise HTTPException(status_code=403)

    return User(**data)


async def _get_current_user_without_error(
    data: Annotated[dict, Depends(http_bearer, use_cache=False)],
) -> User | None:
    return User(**data) if data else None


get_current_user = Annotated[User, Depends(_get_current_user)]
get_current_user_without_error = Annotated[User | None, Depends(_get_current_user_without_error)]
