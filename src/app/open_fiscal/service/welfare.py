from datetime import datetime
from typing import Annotated

from fastapi import Query

from src.app.open_fiscal.repository.welfare import GovWelfareRepository
from src.app.open_fiscal.schema.welfare import WelfareDto
from src.core.dependencies.db import postgres_session


class GovWelfareService:
    def __init__(self, repository: GovWelfareRepository):
        self.repository = repository

    async def get_fiscal(self, session: postgres_session, data: Annotated[WelfareDto, Query()]):
        now = datetime.now()
        age = now.year - data.birthday.year
        age = age if now.month >= data.birthday.month and now.day >= data.birthday.day else age - 1

        result = await self.repository.get_page(
            session,
            data.page,
            data.size,
            [self.repository.model.JA0110 <= age, self.repository.model.JA0111 >= age],
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
