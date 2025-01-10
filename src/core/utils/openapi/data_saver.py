from abc import ABC, abstractmethod
from typing import TypeVar

import polars as pl
import sqlalchemy
from sqlalchemy import Column, Index, Integer, MetaData, Table, delete
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase
from webtool.db import SyncDB

from .data_manager import BaseDataManager

T = TypeVar("T", bound=DeclarativeBase)


class BaseDataSaver(ABC):
    @abstractmethod
    def _save(self, data):
        pass

    @abstractmethod
    def build(self):
        pass


class PostgresDataSaver(BaseDataSaver):
    def __init__(
        self,
        *data: BaseDataManager,
        db: SyncDB,
        table: type[T],
    ):
        self.db = db
        self.manager: tuple[BaseDataManager, ...] = data
        self.table = table

        [m.register_callback(self._callback) for m in self.manager]

    def build(self) -> pl.DataFrame:
        raise NotImplementedError("build method must be implemented by subclass")

    def _callback(self):
        if all(manager.is_initialized for manager in self.manager):
            data = self.build()
            self._save(data)

    def _save(self, data: pl.DataFrame):
        try:
            with self.db.engine.connect() as conn:
                with conn.begin():
                    conn.execute(delete(self.table))
        except sqlalchemy.exc.ProgrammingError:
            pass

        data.write_database(self.table.__tablename__, connection=self.db.engine, if_table_exists="append")


class SQLiteDataSaver(BaseDataSaver):
    """
    SQLiteDataSaver 은 여러 DataManager 로부터 데이터를 구현된 build 메서드로 취합하여 Sqlite DB 에 전송합니다.
    이 과정에서 미리 만들어진 테이블 혹은 자동 생성 방식을 선택할 수 있습니다.

    자동 생성 방식은 table_name가 필요하고, table 의 상태를 수동으로 추적해야 합니다.
    미리 만들어진 테이블을 사용하는 것이 권장됩니다.
    """

    def __init__(
        self,
        *data: BaseDataManager,
        engine: Engine,
        table: type[T] | None = None,
        table_name: str | None = None,
        index: list[str | list[str, str]] | None = None,
        pk: str | None = None,
    ):
        if table is None and table_name is None:
            raise ValueError("table or table_name must be specified")

        self.engine = engine
        self.metadata = MetaData()
        self.pk = pk
        self.table_name = table.__tablename__ if table is not None else table_name
        self.index = index or []
        self.manager: tuple[BaseDataManager, ...] = data
        self.table = table or Table(self.table_name, self.metadata)
        self._has_pre_existing_table = False if table is None else True

        [m.register_callback(self._callback) for m in self.manager]

    def build(self) -> pl.DataFrame:
        raise NotImplementedError("build method must be implemented by subclass")

    def _callback(self):
        if all(manager.is_initialized for manager in self.manager):
            data = self.build()
            if not self._has_pre_existing_table:
                self._build_table(data)
            self._save(data)

    def _build_table(self, data: pl.DataFrame):
        schema = {k: self._polars_dtype_to_dbtype(v) for k, v in data.collect_schema().items()}
        col = []

        if self.pk is None:
            col.append(Column("id", Integer, primary_key=True))
        elif self.pk in schema.keys():
            pk_schema = schema.pop(self.pk)
            col.append(Column(self.pk, getattr(sqlalchemy, pk_schema), primary_key=True))
        else:
            pass

        col.extend([Column(k, getattr(sqlalchemy, v)) for k, v in schema.items()])
        self.table = Table(self.table_name, self.metadata, *col, extend_existing=True)

    def _save(self, data: pl.DataFrame):
        self.table.drop(self.engine, checkfirst=True)
        self.table.create(self.engine)

        def create_index(idx: str | list[str]) -> Index:
            if isinstance(idx, str):
                return Index(f"idx_{idx}", getattr(self.table.c, idx))
            else:
                return Index(f"idx_{"_".join(idx)}", *(getattr(self.table.c, i) for i in idx))

        if not self._has_pre_existing_table:
            [create_index(idx).create(bind=self.engine) for idx in self.index]
            data.write_database(self.table_name, connection=self.engine, if_table_exists="append")

    @staticmethod
    def _polars_dtype_to_dbtype(t: pl.DataType):
        if isinstance(t, pl.Decimal):
            return "NUMERIC"
        elif isinstance(t, (pl.Float32, pl.Float64)):
            return "REAL"
        elif isinstance(t, (pl.Int8, pl.Int16, pl.Int32, pl.Int64, pl.UInt8, pl.UInt16, pl.UInt32, pl.UInt64)):
            return "INTEGER"
        elif isinstance(t, pl.Date):
            return "DATE"
        elif isinstance(t, pl.Datetime):
            return "DATETIME"
        elif isinstance(t, pl.Duration):
            return "TEXT"
        elif isinstance(t, pl.Time):
            return "TIME"
        elif isinstance(t, (pl.Array, pl.List)):
            return "TEXT"
        elif isinstance(t, pl.Struct):
            return "JSON"
        elif isinstance(t, (pl.String, pl.Categorical, pl.Enum, pl.Utf8)):
            return "TEXT"
        elif isinstance(t, pl.Binary):
            return "BLOB"
        elif isinstance(t, pl.Boolean):
            return "INTEGER"
        elif isinstance(t, pl.Null):
            return "NULL"
        elif isinstance(t, pl.Object):
            return "TEXT"
        elif isinstance(t, pl.Unknown):
            return "TEXT"
        else:
            raise TypeError(f"Unknown type: {t}")
