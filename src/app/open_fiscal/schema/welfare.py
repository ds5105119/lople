from pydantic import BaseModel


class WelfareDto(BaseModel):
    birthday: int | None = None
