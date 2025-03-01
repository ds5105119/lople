from typing import Annotated

from fastapi import APIRouter, Depends, status
from webtool.throttle import limiter

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


@limiter(max_requests=10)
@router.post("/refresh", status_code=status.HTTP_200_OK)
async def refresh_tokens(
    response: Annotated[TokenDto, Depends(user_service.refresh_tokens)],
) -> TokenDto:
    return response


@limiter(max_requests=10)
@router.patch("/profile", status_code=status.HTTP_200_OK)
async def update_profile(
    _: Annotated[None, Depends(user_service.update_profile)],
):
    pass


@limiter(max_requests=1, interval=7 * 24 * 60 * 60)
@router.patch("/username", status_code=status.HTTP_200_OK)
async def update_username(
    _: Annotated[None, Depends(user_service.update_username)],
):
    pass


@router.delete("", status_code=status.HTTP_200_OK)
async def delete_user(
    _: Annotated[None, Depends(user_service.delete_user)],
):
    pass


@router.get("/inactive", status_code=status.HTTP_200_OK)
async def inactive_user(
    _: Annotated[None, Depends(user_service.inactive_user)],
):
    pass
