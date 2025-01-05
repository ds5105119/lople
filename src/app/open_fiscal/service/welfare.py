from datetime import datetime
from typing import Annotated

from fastapi import Depends, Query
from sqlalchemy import or_

from src.app.open_fiscal.repository.welfare import GovWelfareRepository
from src.app.open_fiscal.schema.welfare import WelfareDto
from src.app.user.repository.user_data import UserDataRepository
from src.core.dependencies.db import postgres_session
from src.core.dependencies.oauth import get_current_user_without_error


class GovWelfareService:
    def __init__(self, repository: GovWelfareRepository, user_repository: UserDataRepository):
        self.repository = repository
        self.user_data_repository = user_repository

    async def _get_user_data(self, session: postgres_session, auth_data):
        user_data = await self.user_data_repository.get_instance(
            session,
            [self.user_data_repository.model.user_id == int(auth_data.identifier)],
        )

        return user_data.scalar()

    async def get_fiscal(
        self,
        session: postgres_session,
        data: Annotated[WelfareDto, Query()],
        auth_data=Depends(get_current_user_without_error),
    ):
        now = datetime.now()
        age = now.year - data.birthday.year
        age = age if now.month >= data.birthday.month and now.day >= data.birthday.day else age - 1

        user_data = None
        if auth_data:
            user_data = await self._get_user_data(session, auth_data)

        filters = [
            self.repository.model.JA0110 <= age,
            self.repository.model.JA0111 >= age,
        ]

        if user_data:
            filters += [
                self.repository.model.JA0401 == user_data.multicultural,
                self.repository.model.JA0402 == user_data.north_korean,
                self.repository.model.JA0403 == user_data.single_parent_or_grandparent,
                self.repository.model.JA0404 == user_data.single_family,
            ]

        result = await self.repository.get_page(
            session,
            data.page,
            data.size,
            filters,
            [
                self.repository.model.views,
                self.repository.model.service_name,
                self.repository.model.service_summary,
                self.repository.model.service_category,
                self.repository.model.service_conditions,
                self.repository.model.apply_period,
                self.repository.model.apply_url,
                self.repository.model.document,
                self.repository.model.receiving_agency,
                self.repository.model.contact,
                self.repository.model.support_details,
            ],
            [self.repository.model.views.desc()],
        )

        return result.mappings().all()
