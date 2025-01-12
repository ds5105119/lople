from fastapi import APIRouter, Depends, HTTPException
from src.core.config import settings
from src.app.user.schema.user import LoginResponse, LoginResponseUser
from src.app.user.api.dependencies import google_oauth_service
from src.core.utils.googleapi.peopleapi import get_google_userinfo

router = APIRouter()

@router.post("/auth/google", response_model=LoginResponse)
async def google_login(
        authorization_code: str,  # Google Authorization Code from Client
        google_service: Depends(google_oauth_service),
):
    """
    Google OAuth 로그인 엔드포인트
    """
    try:
        # 1: Exchange Authorization Code for Access Token
        token_response = google_service.request_access_token(authorization_code)
        access_token = token_response.get("access_token")
        if not access_token:
            raise HTTPException(status_code=400, detail="Failed to retrieve Google access token")

        # 2: Request UserInfo via Access Token
        user_info = google_service.request_userinfo(access_token)
        google_user_id = user_info.get("id")
        email = user_info.get("email")
        name = user_info.get("name")

        if not google_user_id or not email:
            raise HTTPException(status_code=400, detail="Invalid user info retrieved from Google.")

        # 3: Call google people api (In progress)
        # google_people_api_response = get_google_userinfo(access_token)

        return access_token

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
