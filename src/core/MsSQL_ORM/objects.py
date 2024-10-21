"""SQL工具 物件類別"""
from typing import Self
from typing import Any
from typing import Union
from dataclasses import dataclass,field
from rich.console import Console
from rich.table import Table
from rich.style import Style
import pandas as pd
from .history import HistoryControl

@dataclass
class EXDataBase(): #pylint:disable = R0902
    """資料庫資訊
    """
    _db:Any
    _cursor:Any = field(init=False, default=None)
    _host:str = field(default=None)
    _database:str = field(default=None)
    _table:str = field(default=None)
    _top_layer:str = field(init=False, default=None)
    _history:'HistoryControl' = field(init=False, default=None)
    commit:bool = field(default=True)

    def __post_init__(self) -> None:
        self._cursor = self._db.cursor(as_dict = True)
        self._history = HistoryControl()
        if self.database is not None:
            self._history.create_history(F"{self.database}.historyTable")

    @property
    def db(self) -> Any:
        """資料庫引擎"""
        return self._db

    @property
    def cursor(self) -> Any:
        """資料庫指標"""
        return self._cursor

    @property
    def host(self) -> str:
        """位置"""
        return self._host

    @property
    def database(self) -> str:
        """資料庫"""
        return self._database

    @property
    def table(self) -> str:
        """資料表"""
        return self._table

    @property
    def history(self) -> 'HistoryControl':
        """歷史紀錄"""
        return self._history

    @property
    def top_layer(self) -> str:
        """頂層操作層級"""
        return self._top_layer

class _Extend():
    def __init__(self, ex_database:EXDataBase) -> None:
        self._ex_database:EXDataBase = ex_database

    @property
    def ex_database(self) -> EXDataBase:
        """資料庫資訊(commit屬性可在此設定)

        Returns:
            EXDataBase: 資料庫屬性
        """
        return self._ex_database

    @property
    def commit(self) -> bool:
        """交易成立設置,當為True時才可成立交易. 預設為False

        Returns:
            bool
        """
        return self._ex_database.commit

    @commit.setter
    def commit(self, _:bool) -> None:
        self._ex_database.commit = _

@dataclass
class ColumnInfo():
    """資料表欄位資訊
    """
    name:str
    datatype:str
    nullable:bool

@dataclass
class Condition():
    """條件物件
    """
    column:str
    condition:str
    value:str
    sql_string:str = field(init=False,default=None)

    def __post_init__(self) -> None:
        symbols = [
            '>','>=','=','!=','<=','<','like'
        ]
        self.condition = self.condition.lower()

        if self.condition not in symbols:
            raise ValueError("未知判斷符號")

        if str(self.value)[0] == '*':
            self.sql_string = F"{self.column} {self.condition} {self.value}"
        elif (str(self.value).lower() == 'none' or str(self.value).lower() == 'null'):
            self.sql_string = F"{self.column} is NULL"
        else:
            self.sql_string = F"{self.column} {self.condition} '{self.value}'"


    @staticmethod
    def _addition(
        sql_string:str,
        condition_list:list[Union['Condition',str]]
        ) -> str:

        if len(condition_list) > 1:
            for i in range(0, len(condition_list), 2):
                if i+1 >= len(condition_list):
                    break
                sql_string += F" {condition_list[i].sql_string} {condition_list[i+1]}"

        sql_string += F" {condition_list[-1].sql_string}"

        return sql_string

class Operation():
    """條件式物件\n
    當對欄位使用 比較運算子 時自動轉換為SQL條件語句
    """
    def __init__(self, condition) -> None:
        self._sql_string = condition

    def __repr__(self) -> str:
        return self._sql_string

    def __str__(self) -> str:
        return self._sql_string

    @property
    def sql_string(self):
        """獲取SQL語句"""
        return self._sql_string

    def __or__(self, __value:'Operation') -> Self:
        self._sql_string = F"({self.sql_string} OR {__value.sql_string})"
        return Operation(self.sql_string)

    def __and__(self, __value:'Operation') -> Self:
        self._sql_string = F"({self.sql_string} AND {__value.sql_string})"
        return Operation(self.sql_string)

class QueryResult():
    """搜尋結果處理
    """
    def __init__(self, data_frame:list[dict], title:str = None) -> None:
        self.data_frame :pd.DataFrame = pd.DataFrame(data_frame)
        self.title = title

    @property
    def data(self) -> pd.DataFrame:
        """原始資料

        Returns:
            pd.DataFrame: DataFrame 資料表
        """
        return self.data_frame

    def show(self) -> None:
        """可視化圖表
        """
        console = Console()
        table = Table(show_header=True, title=self.title)
        table.title_style = Style(color='green', bold=True)

        for column in self.data_frame.columns:
            table.add_column(column)

        for row_data in self.data_frame.values:
            row_data = [str(data) for data in row_data]
            row_data = tuple(row_data)

            table.add_row(*row_data)

        console.print(table)
