import datetime
import enum
from typing import Optional

from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, ForeignKeyConstraint, Integer, String, func
from sqlalchemy.ext.mutable import MutableSet
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.app.user.model.user_data import UserData
from src.core.models.base import Base
from src.core.models.helper import IntEnum


class Gender(enum.Enum):
    male = 0
    female = 1


class GenderT(IntEnum):
    _enum_type = Gender


class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    email: Mapped[str] = mapped_column(String(255), unique=True)
    handle: Mapped[str] = mapped_column(String(255), unique=True)
    password: Mapped[str] = mapped_column(String(255))

    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, onupdate=func.now())
    deleted_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)

    resignation_reason: Mapped[Optional[str]] = mapped_column(String(255))

    profile: Mapped["Profile"] = relationship("Profile", back_populates="user", uselist=False)
    user_data: Mapped["UserData"] = relationship("UserData", back_populates="user", uselist=False)


class Profile(Base):
    __tablename__ = "profile"
    __table_args__ = (ForeignKeyConstraint(["user_id"], ["user.id"], name="profiles_user_id_fk", ondelete="CASCADE"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    sex: Mapped["Gender"] = mapped_column(GenderT)
    birthday: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    profile: Mapped[str] = mapped_column(String(255))
    bio: Mapped[Optional[str]] = mapped_column(String(255))
    link: Mapped[Optional[list]] = mapped_column(MutableSet.as_mutable(JSON))

    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    user: Mapped["User"] = relationship("User", back_populates="profile")
