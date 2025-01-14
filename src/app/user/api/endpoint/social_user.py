from fastapi import APIRouter, HTTPException, Depends


router = APIRouter()

@router.post(path="/{provider}", description="social login& register")
async def social_auth(provider: str):
    pass
