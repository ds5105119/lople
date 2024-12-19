from abc import ABC, abstractmethod

import polars as pl
import sqlalchemy
from sqlalchemy import Column, Integer, MetaData, Table
from sqlalchemy.engine import Engine

from .data_manager import BaseDataManager


class BaseDataSaver(ABC):
    @abstractmethod
    def _save(self, data):
        pass

    @abstractmethod
    def build(self):
        pass

    @staticmethod
    @abstractmethod
    def _polars_dtype_to_dbtype(t: pl.DataType):
        pass


class SQLiteDataSaver(BaseDataSaver):
    def __init__(
        self,
        *data: BaseDataManager,
        engine: Engine,
        table_name: str,
        join_by: list[str] | None = None,
        pk: str | None = None,
    ):
        self.engine = engine
        self.metadata = MetaData()
        self.pk = pk
        self.join_by = join_by
        self.table_name = table_name
        self.table = Column(self.table_name, self.metadata)
        self.manager: tuple[BaseDataManager, ...] = data
        self._callback()
        [m.register_callback(self._callback) for m in self.manager]

    def _callback(self):
        data = self.build()
        self._build_table(data)
        self._save(data)

    def build(self) -> pl.DataFrame:
        raise NotImplementedError("build method must be implemented by subclass")

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
        self.table = Table(self.table_name, self.metadata, *col)

    def _save(self, data: pl.DataFrame):
        self.table.drop(self.engine, checkfirst=True)
        self.table.create(self.engine)
        data.write_database(self.table_name, connection=self.engine, if_table_exists="append")

    def join(self, *df: pl.DataFrame):
        table = df[0]
        for frame in df[1:]:
            columns = set(frame.columns) - set(col for col in table.columns if col not in self.join_by)
            table = table.join(frame.select(columns), on=self.join_by, how="left")
        return table

    @staticmethod
    def cast_y_null_to_bool(df: pl.DataFrame):
        is_target = lambda col: col.drop_nulls().unique().len() == 1 and col.drop_nulls().unique()[0] == "Y"
        target = [col for col in df.columns if df[col].dtype == pl.Utf8 and is_target(df[col])]
        converted_df = [pl.when(pl.col(col) == "Y").then(True).otherwise(False).alias(col) for col in target]
        return df.with_columns(converted_df)

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
