import polars as pl

from src.core.utils.openapi.data_helper import cast_y_null_to_bool, join
from src.core.utils.openapi.data_saver import SQLiteDataSaver


class GovWelfare(SQLiteDataSaver):
    def build(self):
        df = join(*[m.data for m in self.manager])
        df = cast_y_null_to_bool(df)
        df = df.filter(pl.col("소관기관유형") == "중앙행정기관")
        return df
