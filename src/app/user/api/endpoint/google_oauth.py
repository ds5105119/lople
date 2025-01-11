from fastapi import APIRouter, status
from src.core.config import settings


router = APIRouter()

GOOGLE_CLIENT_ID = settings.google.client_id
GOOGLE_CLIENT_SECRET = settings.google.secret_key
GOOGLE_REDIRECT_URI = settings.google.redirect_uri

@router.get("/login/google", status_code=status.HTTP_200_OK)
async def login_with_google():
    pass

@router.get("/google/callback", response_model=None)
async def google_oauth_callback():
    pass