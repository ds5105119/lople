from src.core.models.repository import (
    BaseCreateRepository,
    BaseDeleteRepository,
    BaseReadRepository,
    BaseUpdateRepository,
)


class GovWelfareCreateRepository(BaseCreateRepository):
    pass


class GovWelfareReadRepository(BaseReadRepository):
    pass


class GovWelfareUpdateRepository(BaseUpdateRepository):
    pass


class GovWelfareDeleteRepository(BaseDeleteRepository):
    pass


class GovWelfareRepository(
    GovWelfareCreateRepository,
    GovWelfareReadRepository,
    GovWelfareUpdateRepository,
    GovWelfareDeleteRepository,
):
    pass
