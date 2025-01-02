from typing import Annotated, Any

from fastapi import APIRouter, Depends, status
from webtool.throttle import limiter

from src.app.open_fiscal.api.dependencies import gov_welfare_service

router = APIRouter()


@limiter(max_requests=300)
@router.get("/gov")
async def gov_welfare(result: Annotated[Any, Depends(gov_welfare_service.get_fiscal)]):
    return result
