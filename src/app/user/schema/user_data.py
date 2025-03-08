from pydantic import BaseModel, ConfigDict

from src.app.user.model.user_data import AcademicStatus
from src.core.utils.pydantichelper import partial_model


class UserDataDto(BaseModel):
    overcome: int
    household_size: int

    multicultural: bool
    north_korean: bool
    single_parent_or_grandparent: bool
    homeless: bool
    new_resident: bool
    multi_child_family: bool
    extend_family: bool

    disable: bool
    veteran: bool
    disease: bool

    prospective_parents_or_infertility: bool
    pregnant: bool
    childbirth_or_adoption: bool

    farmers: bool
    fishermen: bool
    livestock_farmers: bool
    forestry_workers: bool

    unemployed: bool
    employed: bool

    academic_status: AcademicStatus

    model_config = ConfigDict(use_enum_values=True)


@partial_model
class PartialUserDataDto(UserDataDto):
    pass
