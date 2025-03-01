from typing import Annotated, Any

from fastapi import APIRouter, Depends
from webtool.throttle import limiter

from src.app.open_api.api.dependencies import gov_welfare_service

router = APIRouter()


@limiter(max_requests=300)
@router.get("/gov")
async def gov_welfare(result: Annotated[Any, Depends(gov_welfare_service.get_personal_fiscal)]):
    return result
