import enum
from pydantic import BaseModel, EmailStr

from src.app.user.schema.user import PartialProfileDto


class SocialProvider(enum.Enum):
    """
    지원하는 소셜 로그인 인증 제공자
    """
    GOOGLE = "google"
    KAKAO = "kakao"

class SocialUserVerificationDTO(BaseModel):
    """
    최초 소셜 로그인 User 정보 식별
    """
    email: EmailStr
    social_provider: SocialProvider

class SocialLoginDTO(BaseModel):
    auth_code: str

class SocialUserRegisterDTO(BaseModel):
    email: EmailStr
    username: str
    social_provider: str
    social_id: str
    profile: PartialProfileDto | None = None

