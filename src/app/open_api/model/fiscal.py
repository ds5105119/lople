import polars as pl
from sqlalchemy import Integer, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.core.models.base import Base
from src.core.utils.openapi.data_manager import PolarsDataManager
from src.core.utils.openapi.data_saver import PostgresDataSaver
from src.core.utils.polarshelper import Table


class FiscalDataSaver(PostgresDataSaver):
    def build(self):
        if not self.manager:
            raise RuntimeError("manager not set")

        df: pl.DataFrame = self.manager[0].data
        mappings = [
            ["문화재청", "국가유산청"],
            ["안전행정부", "행정자치부", "행정안전부"],
            ["미래창조과학부", "과학기술정보통신부"],
            ["국가보훈처", "국가보훈부"],
        ]

        department_no = {k: v for v, k in enumerate(set(df.select("OFFC_NM").to_series()))}
        for mapping in mappings:
            min_no = min([department_no[name] for name in mapping if department_no.get(name)])
            department_no.update({name: min_no for name in mapping})

        df = df.with_columns(
            pl.col("OFFC_NM")
            .map_elements(lambda x: department_no.get(x, None), return_dtype=pl.Int8)
            .alias("NORMALIZED_DEPT_NO")
        )

        return df


class Fiscal(Base):
    __tablename__ = "open_fiscal"
    __table_args__ = ()

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    FSCL_YY: Mapped[str] = mapped_column(Text)
    OFFC_NM: Mapped[str] = mapped_column(Text)
    NORMALIZED_DEPT_NO: Mapped[str] = mapped_column(Text)
    FSCL_NM: Mapped[str] = mapped_column(Text)
    ACCT_NM: Mapped[str] = mapped_column(Text, nullable=True)
    FLD_NM: Mapped[str] = mapped_column(Text)
    SECT_NM: Mapped[str] = mapped_column(Text)
    PGM_NM: Mapped[str] = mapped_column(Text)
    ACTV_NM: Mapped[str] = mapped_column(Text)
    SACTV_NM: Mapped[str] = mapped_column(Text)
    BZ_CLS_NM: Mapped[str] = mapped_column(Text)
    FIN_DE_EP_NM: Mapped[str] = mapped_column(Text)
    Y_YY_MEDI_KCUR_AMT: Mapped[str] = mapped_column(Integer)
    Y_YY_DFN_MEDI_KCUR_AMT: Mapped[str] = mapped_column(Integer)


class BaseFiscalData:
    def __init__(self, manager: PolarsDataManager):
        self.data = manager.data


class FiscalData(BaseFiscalData):
    def __init__(self, manager: PolarsDataManager):
        super().__init__(manager)
        self.department_no = {}
        self.by__year = Table({})
        self.by__year__offc_nm = Table({})
        self.manager = manager
        self.manager.register_callback(self._callback)

    def _callback(self):
        print("Manager data updated. Rebuilding FiscalData...")
        self.data = self.manager.data
        self.build()

    def build(self):
        self.department_no = {k: v for v, k in enumerate(set(self.data.select("OFFC_NM").to_series()))}

        mappings = self._get_mappings()
        for mapping in mappings:
            min_no = min([self.department_no[name] for name in mapping if self.department_no.get(name)])
            self.department_no.update({name: min_no for name in mapping})

        self.data = self.data.with_columns(
            pl.col("OFFC_NM")
            .map_elements(lambda x: self.department_no.get(x, None), return_dtype=pl.Int8)
            .alias("NORMALIZED_DEPT_NO")
        )

        self.by__year = self._by__year()
        self.by__year__offc_nm = self._by__year__offc_nm()

    @staticmethod
    def _get_mappings() -> list[list[str]]:
        return [
            ["문화재청", "국가유산청"],
            ["안전행정부", "행정자치부", "행정안전부"],
            ["미래창조과학부", "과학기술정보통신부"],
            ["국가보훈처", "국가보훈부"],
        ]

    def _by__year(self):
        lf = (
            self.data.group_by("FSCL_YY")
            .agg(pl.col("Y_YY_MEDI_KCUR_AMT").sum().alias("TOTAL_AMT"))
            .sort("FSCL_YY")
            .with_columns(pl.col("TOTAL_AMT").pct_change().alias("PCT_CHANGE"))
        )

    def _by__year__offc_nm(self):
        lf = (
            self.data.group_by(["FSCL_YY", "NORMALIZED_DEPT_NO", "OFFC_NM"])
            .agg(pl.col("Y_YY_MEDI_KCUR_AMT").sum().alias("TOTAL_AMT"))
            .sort(["NORMALIZED_DEPT_NO", "FSCL_YY"])
            .with_columns(pl.col("TOTAL_AMT").pct_change().over("NORMALIZED_DEPT_NO").alias("PCT_CHANGE"))
        )
