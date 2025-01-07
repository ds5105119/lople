from datetime import datetime
from typing import Annotated

from fastapi import Depends, Query
from sqlalchemy import and_, or_
from sqlalchemy.orm import selectinload

from src.app.open_fiscal.repository.welfare import GovWelfareRepository
from src.app.open_fiscal.schema.welfare import WelfareDto
from src.app.user.model.user import User
from src.app.user.model.user_data import AcademicStatus, LifeStatus, PrimaryIndustryStatus
from src.app.user.repository.user import UserRepository
from src.core.dependencies.db import postgres_session
from src.core.dependencies.oauth import get_current_user_without_error


class GovWelfareService:
    def __init__(self, repository: GovWelfareRepository, user_repository: UserRepository):
        self.repository = repository
        self.user_repository = user_repository

    async def _get_user(self, session: postgres_session, auth_data) -> User:
        user_data = await self.user_repository.get_instance(
            session,
            [self.user_repository.model.id == int(auth_data.identifier)],
            options=[
                selectinload(self.user_repository.model.user_data),
                selectinload(self.user_repository.model.profile),
            ],
        )

        return user_data.scalar()

    def _family_status_filter(self, user_data):
        return or_(
            self.repository.model.JA0401 == user_data.multicultural,
            self.repository.model.JA0402 == user_data.north_korean,
            self.repository.model.JA0403 == user_data.single_parent_or_grandparent,
            self.repository.model.JA0404 == user_data.single_family,
            self.repository.model.JA0411 == user_data.multi_child_family,
            self.repository.model.JA0412 == user_data.homeless,
            self.repository.model.JA0413 == user_data.new_resident,
            self.repository.model.JA0414 == user_data.extend_family,
            self.repository.model.JA0410
            != all(
                (
                    user_data.multicultural,
                    user_data.north_korean,
                    user_data.single_parent_or_grandparent,
                    user_data.single_family,
                    user_data.multi_child_family,
                    user_data.homeless,
                    user_data.new_resident,
                    user_data.extend_family,
                )
            ),
        )

    def _life_status_filter(self, user_data):
        status_mapping = {
            LifeStatus.prospective_parents_or_infertility: self.repository.model.JA0301,
            LifeStatus.pregnant: self.repository.model.JA0302,
            LifeStatus.childbirth_or_adoption: self.repository.model.JA0303,
        }

        primary_column = status_mapping.get(user_data.primary_industry_status)

        if primary_column:
            return or_(
                primary_column == True,
                and_(*(col == False for col in status_mapping.values())),
            )
        else:
            return or_(
                and_(*(col == True for col in status_mapping.values())),
                and_(*(col == False for col in status_mapping.values())),
            )

    def _primary_industry_status_filter(self, user_data):
        status_mapping = {
            PrimaryIndustryStatus.farmers: self.repository.model.JA0313,
            PrimaryIndustryStatus.fishermen: self.repository.model.JA0314,
            PrimaryIndustryStatus.livestock_farmers: self.repository.model.JA0315,
            PrimaryIndustryStatus.forestry_workers: self.repository.model.JA0316,
        }

        primary_column = status_mapping.get(user_data.primary_industry_status)

        if primary_column:
            return or_(
                primary_column == True,
                and_(*(col == False for col in status_mapping.values())),
            )
        else:
            return or_(
                and_(*(col == True for col in status_mapping.values())),
                and_(*(col == False for col in status_mapping.values())),
            )

    def _academic_status_filter(self, user_data):
        status_mapping = {
            AcademicStatus.elementary_stu: self.repository.model.JA0317,
            AcademicStatus.middle_stu: self.repository.model.JA0318,
            AcademicStatus.high_stu: self.repository.model.JA0319,
            AcademicStatus.university_stu: self.repository.model.JA0320,
        }

        primary_column = status_mapping.get(user_data.primary_industry_status)

        if primary_column:
            return or_(
                self.repository.model.JA0322 == True,
                primary_column == True,
                and_(*(col == False for col in status_mapping.values())),
            )
        else:
            return or_(
                self.repository.model.JA0322 == True,
                and_(
                    self.repository.model.JA0322 == True,
                    *(col == True for col in status_mapping.values()),
                ),
                and_(
                    self.repository.model.JA0322 == True,
                    *(col == False for col in status_mapping.values()),
                ),
            )

    async def get_fiscal(
        self,
        session: postgres_session,
        data: Annotated[WelfareDto, Query()],
        auth=Depends(get_current_user_without_error),
    ):
        now = datetime.now()
        age = now.year - data.birthday.year
        age = age if now.month >= data.birthday.month and now.day >= data.birthday.day else age - 1

        user = None
        if auth:
            user = await self._get_user(session, auth)
            print(user.__dict__, user.user_data.__dict__, sep="\n")

        filters = [
            self.repository.model.JA0110 <= age,
            self.repository.model.JA0111 >= age,
        ]

        if user:
            if f := self._family_status_filter(user.user_data) is not None:
                filters.append(f)
            if f := self._life_status_filter(user.user_data) is not None:
                filters.append(f)
            if f := self._primary_industry_status_filter(user.user_data) is not None:
                filters.append(f)

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
