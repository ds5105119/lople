from typing import Annotated

from fastapi import HTTPException, Query, Request
from pydantic import ValidationError
from sqlalchemy import desc

from src.app.map.schema.map import Coord2AddrDto, Coord2AddrResponse
from src.core.config import settings
from src.core.dependencies.auth import get_current_user
from src.core.dependencies.db import postgres_session


class MapService:
    def __init__(self):
        pass

    async def coord_to_addr(
        self,
        request: Request,
        coord: Annotated[Coord2AddrDto, Query()],
    ) -> Coord2AddrResponse:
        requests_client = request.app.requests_client
        request_headers = {"Authorization": f"KakaoAK {settings.kakao_api.key}"}
        request_params = coord.model_dump()

        response = await requests_client.get(
            "https://dapi.kakao.com/v2/local/geo/coord2address.json",
            headers=request_headers,
            params=request_params,
        )
        data = response.json()
        print(data)

        try:
            return Coord2AddrResponse.model_validate(data)
        except ValidationError as e:
            print(e)
            raise HTTPException(status_code=400, detail="Invalid coordinate")
