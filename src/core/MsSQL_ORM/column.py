"""資料表欄位"""
import pandas as pd

from .abc import ABCColumn
from .checker import commit_protect,commit_protect_
from .objects import _Extend,EXDataBase,ColumnInfo,HistoryControl,Operation
from .sql_type import SQLType
from .history import HistoryAttributes

class Column(ABCColumn,_Extend):

    def __init__(self, ex_database: EXDataBase, column:ColumnInfo) -> None:
        super().__init__(ex_database)
        self.column:ColumnInfo = column
        self._sql_condition:str = None

    def __str__(self) -> str:
        return self.name

    def __eq__(self, __value: object) -> Operation:
        return Operation(F"[{self.ex_database.table}].[{self.name}] = '{__value}'")

    def __ne__(self, __value: object) -> Operation:
        return Operation(F"[{self.ex_database.table}].[{self.name}] != '{__value}'")

    def __lt__(self, __value: object) -> Operation:
        return Operation(F"[{self.ex_database.table}].[{self.name}] < '{__value}'")

    def __gt__(self, __value: object) -> Operation:
        return Operation(F"[{self.ex_database.table}].[{self.name}] > '{__value}'")

    def __le__(self, __value: object) -> Operation:
        return Operation(F"[{self.ex_database.table}].[{self.name}] <= '{__value}'")

    def __ge__(self, __value: object) -> Operation:
        return Operation(F"[{self.ex_database.table}].[{self.name}] >= '{__value}'")

    def __like__(self, __value: object) -> Operation:
        return Operation(F"[{self.ex_database.table}].[{self.name}] LIKE '{__value}'")

    @property
    def datatype(self) -> str:

        return self.column.datatype

    @datatype.setter
    @commit_protect_
    def datatype(self, _type:SQLType) -> None:
        old = self.datatype
        string = F"ALTER TABLE [{self.ex_database.table}] ALTER COLUMN {self.name} {_type}"
        try:
            self.ex_database.cursor.execute(string)
            HistoryControl.add_history(
                self.ex_database.history,
                [
                    self.commit,
                    "diff",
                    F"{self.ex_database.host}:"
                    F"{self.ex_database.database}.{self.ex_database.table}.{self.name}",
                    HistoryAttributes.column_datatype,
                    old,
                    _type
                ]
                )
        except Exception as ex:#pylint:disable = W0718
            print(F"Modify field:\nSQL Command:{string}\nException:{ex}")

    @property
    def name(self) -> str:

        return self.column.name

    @name.setter
    @commit_protect_
    def name(self, _:str):
        old = self.name
        string = F"exec sp_rename '[{self.ex_database.table}].[{self.name}]', '{_}', 'COLUMN'"
        try:
            self.ex_database.cursor.execute(string)
            HistoryControl.add_history(
                self.ex_database.history,
                [
                    self.commit,
                    "diff",
                    F"{self.ex_database.host}:"
                    F"{self.ex_database.database}.{self.ex_database.table}",
                    HistoryAttributes.table_name,
                    old,
                    _
                ]
                )
        except Exception as ex:#pylint:disable = W0718
            print(F"Modify field:\nSQL Command:{string}\nException:{ex}")

    @property
    def nullable(self) -> bool:

        return self.column.nullable

    @nullable.setter
    @commit_protect_
    def nullable(self, _:bool) -> None:

        if _:
            sql_string = F"ALTER TABLE {self.ex_database.table}"\
                F"ALTER COLUMN {self.name} {self.datatype} NULL"
        else:
            sql_string = F"ALTER TABLE {self.ex_database.table}"\
                F"ALTER COLUMN {self.name} {self.datatype} NOT NULL"

        try:
            self.ex_database.cursor.execute(sql_string)

        except Exception as ex:#pylint:disable = W0718
            print(F"Modify field:\nSQL Command:{sql_string}\nException:{ex}")

    @commit_protect
    async def async_drop(self) -> None:

        string = F"ALTER TABLE [{self.ex_database.table}] DROP COLUMN {self.name}"

        self.ex_database.cursor.execute(F"SELECT * FROM {self.ex_database.table}")
        old_data = pd.DataFrame(self.ex_database.cursor.fetchall())

        try:
            self.ex_database.cursor.execute(string)

            for _,row in old_data.iterrows():
                new_row = row.to_dict()
                del new_row[self.name]
                HistoryControl.add_history(
                    self.ex_database.history,
                    [
                        self.commit,
                        "del",
                        F"{self.ex_database.host}:"
                        F"{self.ex_database.database}.{self.ex_database.table}",
                        "Column value",
                        row.to_dict(),
                        new_row
                    ]
                    )

            HistoryControl.add_history(
                self.ex_database.history,
                [
                    self.commit,
                    "del",
                    F"{self.ex_database.host}:"
                    F"{self.ex_database.database}.{self.ex_database.table}",
                    HistoryAttributes.column,
                    F"{self.column}",
                    None
                ]
                )

        except Exception as ex:#pylint:disable = W0718
            print(F"Drop field:\nSQL Command:{string}\nException:{ex}")

    @commit_protect_
    def drop(self) -> None:

        string = F"ALTER TABLE [{self.ex_database.table}] DROP COLUMN {self.name}"

        self.ex_database.cursor.execute(F"SELECT * FROM {self.ex_database.table}")
        old_data = pd.DataFrame(self.ex_database.cursor.fetchall())

        try:
            self.ex_database.cursor.execute(string)

            for _,row in old_data.iterrows():
                new_row = row.to_dict()
                del new_row[self.name]
                HistoryControl.add_history(
                    self.ex_database.history,
                    [
                        self.commit,
                        "del",
                        F"{self.ex_database.host}:"
                        F"{self.ex_database.database}.{self.ex_database.table}",
                        "Column value",
                        row.to_dict(),
                        new_row
                    ]
                    )

            HistoryControl.add_history(
                self.ex_database.history,
                [
                    self.commit,
                    "del",
                    F"{self.ex_database.host}:"
                    F"{self.ex_database.database}.{self.ex_database.table}",
                    HistoryAttributes.column,
                    F"{self.column}",
                    None
                ]
                )

        except Exception as ex:#pylint:disable = W0718
            print(F"Drop field:\nSQL Command:{string}\nException:{ex}")
