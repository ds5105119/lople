from typing import Annotated

from fastapi import APIRouter, Depends, Response, status

from src.app.user.api.dependencies import user_service
from src.app.user.schema.user import LoginResponse

router = APIRouter()


@router.post("/login", status_code=status.HTTP_200_OK)
async def login(
    tokens: Annotated[tuple[str, str], Depends(user_service.login_user)],
    response: Response,
) -> LoginResponse:
    access, refresh = tokens
    response.set_cookie(key="refresh", value=refresh, httponly=True)
    return LoginResponse(access=access)


@router.post("/register", status_code=status.HTTP_200_OK)
async def register(
    tokens: Annotated[tuple[str, str], Depends(user_service.register_user)],
    response: Response,
) -> LoginResponse:
    access, refresh = tokens
    response.set_cookie(key="refresh", value=refresh, httponly=True)
    return LoginResponse(access=access)


@router.post("/profile", status_code=status.HTTP_200_OK)
async def update_profile(
    _: Annotated[None, Depends(user_service.update_profile)],
):
    pass
