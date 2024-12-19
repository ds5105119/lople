from copy import deepcopy
from typing import Callable, Self

import polars as pl


class Table:
    def __init__(self, table: list[dict], columns: list | None = None):
        self.table: list[dict] = table
        self.columns = columns or list(range(len(self.table[0]))) if self.table else []

    def __repr__(self):
        return self.table.__repr__()

    def __copy__(self):
        return Table(self.table.copy())

    def __getitem__(self, item):
        if isinstance(item, tuple):
            if len(item) != 2:
                raise IndexError("Unsupported indexing")
            row, col = item
            if isinstance(row, int) and isinstance(col, int):
                table = self.table[row][col]
            elif isinstance(row, int) and isinstance(col, slice):
                table = self.table[row][col]
            elif isinstance(row, slice) and isinstance(col, int):
                table = [row[col] for row in self.table[row]]
            elif isinstance(row, slice) and isinstance(col, slice):
                table = [row[col] for row in self.table[row]]
            else:
                raise ValueError("Unsupported indexing")
        elif isinstance(item, (int, slice)):
            table = self.table[item]
        else:
            table = self.table[self._get_idx(item)]

        return Table(table, self.columns)

    def _get_idx(self, col):
        try:
            return self.columns.index(col)
        except ValueError:
            raise IndexError(f"Index {col} not in {self.columns}")

    def filter(self, func: Callable):
        cp = self.__copy__()
        cp.table = filter(func, cp.table)
        return cp

    def sort(self, func: Callable, reverse: bool = False):
        cp = self.__copy__()
        cp.table = sorted(cp.table, key=func, reverse=reverse)
        return cp

    def limit(self, n: int, m: int):
        cp = self.__copy__()
        cp.table = cp.table[n:m]
        return cp

    def collect(self):
        return Table(list(self.table))

    def to_dict(self):
        return self.table

    @classmethod
    def from_pandas(cls, frame: pl.LazyFrame | pl.DataFrame) -> Self:
        if isinstance(frame, pl.LazyFrame):
            frame = frame.collect()

        return cls(frame.to_dicts(), frame.columns)
