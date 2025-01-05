from src.app.user.model.user_data import UserData
from src.core.models.repository import (
    ABaseCreateRepository,
    ABaseDeleteRepository,
    ABaseReadRepository,
    ABaseUpdateRepository,
)


class UserDataCreateRepository(ABaseCreateRepository[UserData]):
    pass


class UserDataReadRepository(ABaseReadRepository[UserData]):
    pass


class UserDataUpdateRepository(ABaseUpdateRepository[UserData]):
    pass


class UserDataDeleteRepository(ABaseDeleteRepository[UserData]):
    pass


class UserDataRepository(
    UserDataCreateRepository,
    UserDataReadRepository,
    UserDataUpdateRepository,
    UserDataDeleteRepository,
):
    pass
