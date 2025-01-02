from datetime import date

from pydantic import BaseModel, Field


class WelfareDto(BaseModel):
    page: int = Field(0, ge=0, description="Page number")
    size: int = Field(10, ge=10, le=10, description="Page size")
    birthday: date | None = None
