import enum
from pydantic import BaseModel, ConfigDict
from src.app.user.schema.user import PartialProfileDto

class SocialProvider(enum.Enum):
    google = 'google'
    kakao = 'kakao'

class UserType(enum.Enum):
    social = 'social'
    general = 'general'

class SocialUserRegisterDTO(BaseModel):
    email: str
    username: str
    social_provider: str
    social_id: str
    profile: PartialProfileDto | None = None


class SocialUserVerificationDTO(BaseModel):
    email: str
    social_id: str
    social_provider: SocialProvider
    user_type: UserType


class SocialUserInfoResponse(BaseModel):
    email: str
    username: str
    social_id: str
    profile: PartialProfileDto | None = None


# test
class GoogleAuthResponse(BaseModel):
    test_data: dict