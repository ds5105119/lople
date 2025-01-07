import enum
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, ForeignKeyConstraint, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.models.base import Base
from src.core.models.helper import IntEnum

if TYPE_CHECKING:
    from src.app.user.model.user import User


class LifeStatus(enum.Enum):
    none = 0
    prospective_parents_or_infertility = 1
    pregnant = 2
    childbirth_or_adoption = 3


class LifeStatusT(IntEnum):
    _enum_type = LifeStatus


class PrimaryIndustryStatus(enum.Enum):
    none = 0
    farmers = 1
    fishermen = 2
    livestock_farmers = 3
    forestry_workers = 4


class PrimaryIndustryStatusT(IntEnum):
    _enum_type = PrimaryIndustryStatus


class AcademicStatus(enum.Enum):
    none = 0
    elementary_stu = 1
    middle_stu = 2
    high_stu = 3
    university_stu = 4


class AcademicStatusT(IntEnum):
    _enum_type = AcademicStatus


class WorkingStatus(enum.Enum):
    none = 0
    unemployed = 1
    employed = 2


class WorkingStatusT(IntEnum):
    _enum_type = WorkingStatus


class UserData(Base):
    __tablename__ = "user_data"
    __table_args__ = (ForeignKeyConstraint(["user_id"], ["user.id"], name="profiles_user_id_fk", ondelete="CASCADE"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    overcome: Mapped[int] = mapped_column(Integer, nullable=True)

    multicultural: Mapped[bool] = mapped_column(Boolean, default=False)
    north_korean: Mapped[bool] = mapped_column(Boolean, default=False)
    single_parent_or_grandparent: Mapped[bool] = mapped_column(Boolean, default=False)
    homeless: Mapped[bool] = mapped_column(Boolean, default=False)
    new_resident: Mapped[bool] = mapped_column(Boolean, default=False)
    multi_child_family: Mapped[bool] = mapped_column(Boolean, default=False)
    single_family: Mapped[bool] = mapped_column(Boolean, default=False)
    extend_family: Mapped[bool] = mapped_column(Boolean, default=False)

    life_status: Mapped[int] = mapped_column(Integer, default=0)
    primary_industry_status: Mapped[int] = mapped_column(Integer, default=0)
    academic_status: Mapped[int] = mapped_column(Integer, default=0)
    working_status: Mapped[int] = mapped_column(Integer, default=0)

    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), unique=True, nullable=False)
    user: Mapped["User"] = relationship("User", back_populates="user_data")
