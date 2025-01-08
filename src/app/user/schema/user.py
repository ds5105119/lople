from typing import Annotated

from argon2 import PasswordHasher
from pydantic import (
    AnyUrl,
    BaseModel,
    EmailStr,
    Field,
    PastDate,
    PlainSerializer,
    UrlConstraints,
    field_validator,
    model_validator,
)
from typing_extensions import Self

from src.app.user.model.user import Gender
from src.core.utils.pydantichelper import partial_model

ph = PasswordHasher()


class HttpUrl(AnyUrl):
    _constraints = UrlConstraints(max_length=255, allowed_schemes=["http", "https"])


class ProfileDto(BaseModel):
    sex: Annotated[Gender, PlainSerializer(lambda x: x.value, return_type=int)]
    birthday: PastDate
    profile: Annotated[HttpUrl, PlainSerializer(lambda x: x.unicode_string(), return_type=str)]
    bio: str = Field(min_length=0, max_length=120)
    link: Annotated[HttpUrl, PlainSerializer(lambda x: x.unicode_string(), return_type=str)]


@partial_model
class PartialProfileDto(ProfileDto):
    pass


class RegisterDto(BaseModel):
    email: EmailStr
    username: str
    password1: str = Field(min_length=8, max_length=30, serialization_alias="password")
    password2: str = Field(min_length=8, max_length=30, exclude=True)
    profile: PartialProfileDto | None = None

    @field_validator("password1")
    @classmethod
    def validate(cls, value: str):
        if value.isalpha():
            raise ValueError("password must contain numbers.")
        if value.isdigit():
            raise ValueError("password must contain letters.")
        return value

    @model_validator(mode="after")
    def check_passwords_match(self) -> Self:
        pw1 = self.password1
        pw2 = self.password2
        if pw1 is not None and pw2 is not None and pw1 != pw2:
            raise ValueError("passwords do not match")
        return self


class LoginDto(BaseModel):
    email: EmailStr | None = None
    username: str | None = None
    password: str = Field(min_length=8, max_length=30)

    @model_validator(mode="after")
    def check_email_or_handle(self) -> Self:
        if not (self.email or self.username):
            raise ValueError("email and handle is empty.")
        return self


class LoginResponse(BaseModel):
    access: str
    refresh: str | None = None
