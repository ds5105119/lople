from fastapi import APIRouter

from .open_api.api.endpoint.fiscal import router as fiscal_router
from .open_api.api.endpoint.welfare import router as welfare_router
from .user.api.endpoint.user import router as user_router
from .user.api.endpoint.user_data import router as user_data_router
from src.app.user.api.endpoint.google_oauth import router as google_router

router = APIRouter()

router.include_router(user_router, prefix="/user", tags=["user"])
router.include_router(user_data_router, prefix="/user/data", tags=["user_data"])
router.include_router(fiscal_router, prefix="/fiscal", tags=["fiscal"])
router.include_router(welfare_router, prefix="/welfare", tags=["welfare"])
router.include_router(google_router, prefix="/oauth/google", tags=["google_oauth"])