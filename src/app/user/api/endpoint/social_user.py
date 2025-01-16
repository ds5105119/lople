from fastapi import APIRouter

router = APIRouter()


@router.post("/oauth/google")
async def google_auth():
    pass
