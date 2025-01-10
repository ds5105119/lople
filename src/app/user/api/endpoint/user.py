from typing import Annotated

from fastapi import APIRouter, Depends, status

from src.app.user.api.dependencies import user_service
from src.app.user.schema.user import LoginResponse, TokenDto

router = APIRouter()


@router.post("/login", status_code=status.HTTP_200_OK)
async def login(
    response: Annotated[LoginResponse, Depends(user_service.login_user)],
) -> LoginResponse:
    return response


@router.post("/register", status_code=status.HTTP_200_OK)
async def register(
    response: Annotated[LoginResponse, Depends(user_service.register_user)],
) -> LoginResponse:
    return response


@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(
    _: Annotated[None, Depends(user_service.logout_user)],
):
    pass


@router.post("/refresh", status_code=status.HTTP_200_OK)
async def refresh_tokens(
    response: Annotated[TokenDto, Depends(user_service.refresh_tokens)],
) -> TokenDto:
    return response


@router.patch("/profile", status_code=status.HTTP_200_OK)
async def update_profile(
    _: Annotated[None, Depends(user_service.update_profile)],
):
    pass
