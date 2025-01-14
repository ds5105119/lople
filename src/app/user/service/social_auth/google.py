import httpx
from typing import Optional
from datetime import datetime
from .base import SocialAuthBase
from src.app.user.schema.social_user import (
    SocialUserRegisterDTO as SocialUser,
    SocialProvider
)
from src.core.config import settings


class GoogleAuth(SocialAuthBase):
    """
    Google 소셜 로그인 구현
    """
    @staticmethod
    def parse_gender(gender: Optional[str]) -> Optional[int]:
        """
        입력된 문자열 형태의 'gender' 값을 Profile 모델의 'sex' (0, 1)로 변환.
        """
        gender_map = {
            "male": 0,
            "female": 1
        }
        return gender_map.get(gender.lower()) if gender else None

    @staticmethod
    def parse_birthday(birthday: Optional[str]) -> Optional[datetime]:
        """
        `YYYY-MM-DD` 형식의 문자열을 `datetime` 객체로 변환.
        """
        try:
            return datetime.strptime(birthday, "%Y-%m-%d") if birthday else None
        except ValueError:
            return None

    async def get_access_token(self, code: str) -> str:
        """
        Google 인증 코드에서 Access Token 반환
        """
        url = "https://oauth2.googleapis.com/token"
        payload = {
            "client_id": settings.oauth_google.client_id,
            "client_secret": settings.oauth_google.secret_key,
            "redirect_uri": settings.oauth_google.redirect_uri,
            "code": code,
            "grant_type": "authorization_code",
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(url, data=payload)
            response.raise_for_status()
            return response.json()["access_token"]

    async def get_user_info(self, access_token: str) -> SocialUser:
        """
        Google Access Token으로 사용자 정보 가져오기
        """
        url = settings.oauth_google.user_info_url
        headers = {"Authorization": f"Bearer {access_token}"}
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()

        user_data = response.json()
        return SocialUser(
            email=user_data["email"],
            username=user_data["name"],
            social_id=user_data["id"],
            social_provider=SocialProvider.GOOGLE.value,
        )

    async def get_user_info_with_people_api(self, access_token: str):
        """
        Google People API를 통해 gender 및 birthday 정보 가져오기
        """
        url = settings.oauth_google.people_api_url
        headers = {"Authorization": f"Bearer {access_token}"}
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            user_info = response.json()

        genders = user_info.get("genders", [])
        birthdays = user_info.get("birthdays", [])

        # 성별 필터링 및 변환
        gender_str = genders[0]["value"].lower() if genders else None
        gender = self.parse_gender(gender_str)

        # 생일 필터링 및 변환
        birthday = None
        if birthdays:
            date = birthdays[0].get("date", {})
            if "year" in date and "month" in date and "day" in date:
                birthday_str = f"{date['year']}-{date['month']}-{date['day']}"
                birthday = self.parse_birthday(birthday_str)

        return {"gender": gender, "birthday": birthday}

