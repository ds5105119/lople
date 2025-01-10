from fastapi import APIRouter, status, HTTPException, Request, Depends
from fastapi.responses import RedirectResponse

from src.core.dependencies.db import postgres_session
from src.core.dependencies.oauth import google_oauth_schema
from src.app.user.repository.user import UserRepository
from src.core.config import settings

from webtool.auth import JWTService

import requests

router = APIRouter()

GOOGLE_CLIENT_ID = settings.GOOGLE_CLIENT_ID
GOOGLE_CLIENT_SECRET = settings.GOOGLE_CLIENT_SECRET
GOOGLE_REDIRECT_URI = settings.GOOGLE_REDIRECT_URI

@router.get("/login/google", status_code=status.HTTP_200_OK)
async def login_with_google():
    google_oauth_url  = (
        f"{google_oauth_schema.authorizationUrl}?"
        f"client_id={GOOGLE_CLIENT_ID}&"
        f"redirect_uri={GOOGLE_REDIRECT_URI}&"
        f"response_type=code&"
        f"scope=openid email profile"
    )
    return RedirectResponse(google_oauth_url)

@router.get("/google/callback")
async def google_callback(
        request: Request,
        session: postgres_session = Depends(postgres_session),
        jwt_service: JWTService = Depends(JWTService),
        user_repository: UserRepository = Depends(UserRepository),
):
    # 1.Get Auth code
    authorization_code = request.query_params.get("code")
    if not authorization_code:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

    # 2. Request Access Token
    token_url = google_oauth_schema.tokenUrl

    data = {
        "grant_type": "authorization_code",
        "code": authorization_code,
        "redirect_uri": GOOGLE_REDIRECT_URI,
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
    }

    # Request POST to Google
    token_response = requests.post(token_url, data=data)
    token_data = token_response.json()

    if "access_token" not in token_data:
        raise HTTPException(status_code=400, detail="Failed to retrieve Google access token")

    # 3. Request user info
    access_token = token_data["access_token"]

    userinfo_url = "https://www.googleapis.com/oauth2/v2/userinfo"
    headers = {"Authorization": f"Bearer {access_token}"}

    userinfo_response = requests.get(userinfo_url, headers=headers)
    userinfo = userinfo_response.json()

    if "email" not in userinfo:
        raise HTTPException(status_code=400, detail="Failed to retrieve user info")

    email = userinfo["email"]
    name = userinfo.get("name", "Unknown User")

    # 4. Save user's data
    user = await user_repository.get_user_by_email(session, email)
    if not user:
        # 4-1. Create new user
        user = await user_repository.create(session, email=email, username=name)
        await session.refresh(user)

    # 5. Issue JWT token
    jwt_payload = {"sub": str(user.id), "email": user.email}
    access_token, refresh_token = await jwt_service.create_token(jwt_payload)

    return {"access_token": access_token, "user": {"email": user.email, "name": name}}