import enum
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr


class SocialProvider(enum.Enum):
    GOOGLE = "google"
    KAKAO = "kakao"

class SocialLoginDTO(BaseModel):
    auth_code: str

class SocialUserCreateDTO(BaseModel):
    email: EmailStr
    username: str
    social_provider: str
    social_id: str
    sex: Optional[int] = None
    birthday: Optional[datetime] = None