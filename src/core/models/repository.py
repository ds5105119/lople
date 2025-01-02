from typing import Any, Sequence, TypeVar, cast

from sqlalchemy import Result, SQLColumnExpression, asc, delete, desc, func, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase, Session

T = TypeVar("T", bound=DeclarativeBase)
_P = Result[tuple[Any]]


class BaseRepository[T]:
    model: type[T]
    session: type[Session]

    def __init__(self, model: type[T]):
        self.model = model

    def get_columns(self, columns: list[str] | None) -> list:
        if columns:
            return [getattr(self.model, column) for column in columns]
        return [self.model]


class BaseCreateRepository[T](BaseRepository[T]):
    def _create(self, session: Session, **kwargs: Any) -> T:
        session.add(entity := self.model(**kwargs))
        session.commit()
        session.refresh(self.model)

        return entity

    def _bulk_create(self, session: Session, kwargs: Sequence[dict[str, Any]]) -> None:
        stmt = insert(self.model).values(kwargs)
        session.execute(stmt)
        session.commit()

    def create(self, session: Session, values: Sequence[dict[str, Any]], **kwargs: Any) -> T:
        if kwargs:
            return self._create(session, **kwargs)
        elif values:
            return self._bulk_create(session, values)
        else:
            raise ValueError("Invalid arguments for creation.")


class BaseReadRepository[T](BaseRepository[T]):
    def get(
        self,
        session: Session,
        filters: Sequence,
        columns: list[SQLColumnExpression] | None = None,
        order_by: list[str] | None = None,
    ) -> _P:
        columns = columns or self.model

        stmt = select(*columns).where(*filters)
        if order_by is not None:
            stmt = stmt.order_by(*order_by)
        result = session.execute(stmt)

        return result

    def get_by_id(
        self,
        session: Session,
        id: int | str,
        columns: list[SQLColumnExpression] | None = None,
        order_by: list[str] | None = None,
    ) -> _P:
        columns = columns or self.model

        stmt = select(*columns).where(cast("ColumnElement[bool]", self.model.id == id))
        if order_by is not None:
            stmt = stmt.order_by(*order_by)
        result = session.execute(stmt)

        return result

    def get_page(
        self,
        session: Session,
        page: int,
        size: int,
        filters: Sequence,
        columns: list[SQLColumnExpression] | None = None,
        order_by: list[str] | None = None,
    ) -> _P:
        columns = columns or self.model

        stmt = select(*columns).where(*filters).fetch(size).offset(page * size)
        if order_by is not None:
            stmt = stmt.order_by(*order_by)
        results = session.execute(stmt)

        return results


class BaseUpdateRepository[T](BaseRepository[T]):
    def filter(self, session: Session, filters: Sequence, **kwargs) -> None:
        query = update(self.model).where(*filters).values(**kwargs)
        session.execute(query)
        session.commit()

    def update_by_id(self, session: Session, id: int | str, **kwargs) -> None:
        query = update(self.model).where(cast("ColumnElement[bool]", self.model.id == id)).values(**kwargs)
        session.execute(query)
        session.commit()


class BaseDeleteRepository[T](BaseRepository[T]):
    def _delete(self, session: Session, id: int | str) -> None:
        stmt = delete(self.model).where(cast("ColumnElement[bool]", self.model.id == id))
        session.execute(stmt)
        session.commit()

    def _bulk_delete(self, session: Session, ids: list[int | str]) -> None:
        stmt = delete(self.model).where(cast("ColumnElement[bool]", self.model.id.in_(ids)))
        session.execute(stmt)
        session.commit()

    def delete(self, session: Session, id: int | str | tuple[int | str] | list[int | str]) -> None:
        if isinstance(id, (int, str)):
            self._delete(session, id)
        elif isinstance(id, (tuple, list)) and len(id):
            self._bulk_delete(session, list(id))
        else:
            raise ValueError("'id' must be an int, str, or Iterable of int or str")


class ABaseRepository[T](BaseRepository[T]):
    session: type[AsyncSession]


class ABaseCreateRepository[T](ABaseRepository[T]):
    async def _create(self, session: AsyncSession, **kwargs: Any) -> T:
        session.add(entity := self.model(**kwargs))
        await session.commit()
        await session.refresh(entity)

        return entity

    async def _bulk_create(self, session: AsyncSession, kwargs: Sequence[dict[str, Any]]) -> None:
        stmt = insert(self.model).values(kwargs)
        await session.execute(stmt)
        await session.commit()

    async def create(
        self,
        session: AsyncSession,
        values: Sequence[dict[str, Any]] | None = None,
        **kwargs: Any,
    ) -> T | None:
        if kwargs:
            return await self._create(session, **kwargs)
        elif values:
            return await self._bulk_create(session, values)
        else:
            raise ValueError("Invalid arguments for creation.")


class ABaseReadRepository[T](ABaseRepository[T]):
    async def get(
        self,
        session: AsyncSession,
        filters: Sequence,
        columns: list[SQLColumnExpression] | None = None,
        order_by: list[str] | None = None,
    ) -> _P:
        columns = self.get_columns(columns)

        stmt = select(*columns).where(*filters)
        if order_by is not None:
            stmt = stmt.order_by(*order_by)
        result = await session.execute(stmt)

        return result

    async def get_by_id(
        self,
        session: AsyncSession,
        id: int | str,
        columns: list[SQLColumnExpression] | None = None,
        order_by: list[SQLColumnExpression] | None = None,
    ) -> _P:
        columns = self.get_columns(columns)

        stmt = select(*columns).where(cast("ColumnElement[bool]", self.model.id == id))
        if order_by is not None:
            stmt = stmt.order_by(*order_by)
        result = await session.execute(stmt)

        return result

    async def get_page(
        self,
        session: AsyncSession,
        page: int,
        size: int,
        filters: Sequence,
        columns: list[SQLColumnExpression] | None = None,
        order_by: list[SQLColumnExpression] | None = None,
    ) -> _P:
        columns = columns or self.model

        stmt = select(*columns).where(*filters).fetch(size).offset(page * size)
        if order_by is not None:
            stmt = stmt.order_by(*order_by)
        results = await session.execute(stmt)

        return results


class ABaseUpdateRepository[T](ABaseRepository[T]):
    async def filter(self, session: AsyncSession, filters: Sequence, **kwargs) -> None:
        query = update(self.model).where(*filters).values(**kwargs)
        await session.execute(query)
        await session.commit()

    async def update_by_id(self, session: AsyncSession, id: int | str, **kwargs) -> None:
        query = update(self.model).where(cast("ColumnElement[bool]", self.model.id == id)).values(**kwargs)
        await session.execute(query)
        await session.commit()


class ABaseDeleteRepository[T](ABaseRepository[T]):
    async def _delete(self, session: AsyncSession, id: int | str) -> None:
        stmt = delete(self.model).where(cast("ColumnElement[bool]", self.model.id == id))
        await session.execute(stmt)
        await session.commit()

    async def _bulk_delete(self, session: AsyncSession, ids: list[int | str]) -> None:
        stmt = delete(self.model).where(cast("ColumnElement[bool]", self.model.id.in_(ids)))
        await session.execute(stmt)
        await session.commit()

    async def delete(self, session: AsyncSession, id: int | str | tuple[int | str] | list[int | str]) -> None:
        if isinstance(id, (int, str)):
            await self._delete(session, id)
        elif isinstance(id, (tuple, list)) and len(id):
            await self._bulk_delete(session, list(id))
        else:
            raise ValueError("'id' must be an int, str, or Iterable of int or str")
