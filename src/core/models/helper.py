from sqlalchemy import event
from sqlalchemy.orm import ORMExecuteState, Session, with_loader_criteria

from src.app.user.model.user import User


@event.listens_for(Session, "do_orm_execute")
def _do_orm_execute(orm_execute_state: ORMExecuteState):
    if orm_execute_state.is_select and not orm_execute_state.is_column_load:
        orm_execute_state.statement = orm_execute_state.statement.options(
            with_loader_criteria(
                User,
                User.is_deleted is False,
                User.is_active is True,
            )
        )
