import polars as pl

from src.core.utils.openapi.data_manager import PolarsDataManager
from src.core.utils.polarshelper import Table


class FiscalData:
    def __init__(
        self,
        service_list: PolarsDataManager,
        service_detail: PolarsDataManager,
        service_condition: PolarsDataManager,
    ):
        self.service_list = service_list
        self.service_detail = service_detail
        self.service_condition = service_condition

        self.service_list.register_callback(self._callback)
        self.service_detail.register_callback(self._callback)
        self.service_condition.register_callback(self._callback)

    def _callback(self):
        print("Manager data updated. Rebuilding FiscalData...")
        self.data = self.service_list.data.join(self.service_detail.data, how="left")
        self.data = self.data.join(self.service_condition.data, how="left")
        self.build()

    def build(self):
        pass
