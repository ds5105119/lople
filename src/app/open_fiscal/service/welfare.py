from src.app.open_fiscal.repository.welfare import GovWelfareRepository
from src.app.open_fiscal.schema.welfare import WelfareDto
from src.core.dependencies.db import sqlite_session


class GovWelfareService:
    def __init__(self, repository: GovWelfareRepository):
        self.repository = repository

    def get_fiscal(self, session: sqlite_session, data: WelfareDto):
        return self.repository.get(session, data)
