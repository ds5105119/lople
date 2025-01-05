from pydantic import BaseModel

from src.app.user.model.user_data import AcademicStatus, LifeStatus, PrimaryIndustryStatus, WorkingStatus
from src.core.utils.pydantichelper import partial_model


class UserDataDto(BaseModel):
    overcome: int

    multicultural: bool
    north_korean: bool
    single_parent_or_grandparent: bool
    homeless: bool
    new_resident: bool
    multi_child_family: bool
    single_family: bool
    extend_family: bool

    life_status: LifeStatus
    primary_industry_status: PrimaryIndustryStatus
    academic_status: WorkingStatus
    working_status: AcademicStatus

    class Config:
        use_enum_values = True


@partial_model
class PartialUserDataDto(UserDataDto):
    pass
