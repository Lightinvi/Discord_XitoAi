"""SQL工具 資料表類別"""
from typing import Any
import pandas as pd

from .abc import ABCTable,ABCVTable
from .crud import _Select,_Update,_Insert,_Delete
from .column import Column
from .objects import EXDataBase,ColumnInfo,HistoryControl
from .sql_type import SQLType
from .checker import commit_protect, commit_protect_
from .history import HistoryAttributes

class Table(ABCTable):
    """database工作表"""
    def __init__(self, ex_database:EXDataBase) -> None:
        self._ex_database:EXDataBase = ex_database
        self._ex_database._table = ex_database.table
        self._layer = "Table"
        for column in self._columns:
            if column.name in ('ex_database', 'layer', 'commit', 'name'):
                setattr(self,F"{column.name}_",Column(self.ex_database, column))
            else:
                setattr(self,column.name,Column(self.ex_database, column))

    @property
    def ex_database(self) -> EXDataBase:
        """資料庫資訊

        Returns:
            EXDataBase: 資料庫屬性
        """
        return self._ex_database

    @property
    def layer(self) -> str:
        """操作層級"""
        return self._layer

    @property
    def commit(self) -> bool:
        """交易成立設置,當為True時才可成立交易. 預設為False

        Returns:
            bool
        """
        return self._ex_database.commit

    @commit.setter
    def commit(self, _:bool) -> None:
        if not isinstance(_,bool):
            raise TypeError
        self._ex_database.commit = _

    @property
    def name(self) -> str:
        return self.ex_database.table

    @name.setter
    @commit_protect_
    def name(self, _:str) -> None:
        old = self.name
        string = F"EXEC sp_rename '[{self.name}]', '{_}'"
        try:
            self.ex_database.cursor.execute(string)
            self._ex_database._table = _ #pylint:disable=w0212
            self.ex_database.history.add_history(
                [
                    self.commit,
                    "diff",
                    F"{self.ex_database.host}:"
                    F"{self.ex_database.database}",
                    HistoryAttributes.table_name,
                    old,
                    _
                ]
                )
        except Exception as ex:#pylint:disable = W0718
            print(F"Modify field:\nSQL Command:{string}\nException:{ex}")

    @property
    def columns(self) -> tuple[str]:

        return tuple(
            column.name
            if column.name not in ('ex_database', 'layer', 'commit', 'name')
            else F"{column.name}_"
            for column in self._columns
            )

    @property
    def _columns(self) -> tuple[ColumnInfo]:

        self.ex_database.cursor.execute(
            "SELECT COLUMN_NAME,IS_NULLABLE,DATA_TYPE,"
            "CHARACTER_MAXIMUM_LENGTH,NUMERIC_PRECISION, NUMERIC_SCALE,DATETIME_PRECISION"
            F" FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '{self.ex_database.table}'"
        )
        column_list = []
        for table in self._ex_database.cursor.fetchall():

            if table['CHARACTER_MAXIMUM_LENGTH'] is not None:
                length = table['CHARACTER_MAXIMUM_LENGTH']

            elif table['NUMERIC_PRECISION'] and table['NUMERIC_SCALE'] is not None\
            and table['NUMERIC_SCALE'] != 0:
                length = F"{table['NUMERIC_PRECISION']}, {table['NUMERIC_SCALE']}"

            elif table['NUMERIC_PRECISION'] and table['NUMERIC_SCALE'] is not None\
            and table['NUMERIC_SCALE'] == 0:
                length = ""

            elif table['NUMERIC_PRECISION'] is not None and table['NUMERIC_SCALE'] is None:
                length = table['NUMERIC_PRECISION']

            elif table['DATETIME_PRECISION'] is not None:
                length = table['DATETIME_PRECISION']

            else:
                length = ""

            column_list.append(
                ColumnInfo(
                    table['COLUMN_NAME'],
                    F"{table['DATA_TYPE']}({length})",
                    table['IS_NULLABLE']
                )
            )

        return tuple(column_list)

    def select(self, *args, **kwargs) -> _Select:
        return _Select(self.ex_database, *args, **kwargs)

    def update(self, **columns:Any) -> _Update:

        return _Update(self.ex_database, **columns)

    def insert(self, *columns:Column|str) -> _Insert:

        return _Insert(self.ex_database, *columns)

    def delete(self, quantity:int = -1) -> _Delete:

        return _Delete(self.ex_database, quantity)

    @commit_protect
    async def async_truncate(self) -> None:
        sql_string = F"TRUNCATE TABLE {self.name}"

        result = await self.select().result
        result = result.data

        try:
            self.ex_database.cursor.execute(sql_string)

            for _,old_row in result.iterrows():
                old_row = old_row.to_list()
                self.ex_database.history.add_history(
                [
                    self.commit,
                    "del",
                    F"{self.ex_database.host}:"
                    F"{self.ex_database.database}.{self.ex_database.table}",
                    HistoryAttributes.column_value,
                    old_row,
                    None
                ]
                )

        except Exception as ex:#pylint:disable = W0718
            print(F"Truncate failed:\nSQL Command:{sql_string}\nException:{ex}")

    @commit_protect_
    def truncate(self) -> None:
        sql_string = F"TRUNCATE TABLE {self.name}"

        result = self.select().result
        result = result.data

        try:
            self.ex_database.cursor.execute(sql_string)

            for _,old_row in result.iterrows():
                old_row = old_row.to_list()
                self.ex_database.history.add_history(
                [
                    self.commit,
                    "del",
                    F"{self.ex_database.host}:"
                    F"{self.ex_database.database}.{self.ex_database.table}",
                    HistoryAttributes.column_value,
                    old_row,
                    None
                ]
                )

        except Exception as ex:#pylint:disable = W0718
            print(F"Truncate failed:\nSQL Command:{sql_string}\nException:{ex}")

    @commit_protect
    async def async_backup(
        self,
        new_table:str,
        *,
        copy_data:bool = True
        ) -> None:

        string = F"SELECT * INTO {new_table} FROM {self.ex_database.table}"
        if not copy_data:
            string += " WHERE 1=0"

        try:
            self.ex_database.cursor.execute(string)

            self.ex_database.history.add_history(
                [
                    self.commit,
                    "new",
                    F"{self.ex_database.host}:"
                    F"{self.ex_database.database}",
                    HistoryAttributes.table,
                    None,
                    new_table
                ]
                )

            if copy_data:
                self.ex_database.cursor.execute(F"SELECT * FROM {new_table}")
                result = pd.DataFrame(self.ex_database.cursor.fetchall())

                for _, row in result.iterrows():
                    self.ex_database.history.add_history(
                        [
                            self.commit,
                            "new",
                            F"{self.ex_database.host}:"
                            F"{self.ex_database.database}."
                            F"{new_table}",
                            HistoryAttributes.column_value,
                            None,
                            row.to_list()
                        ]
                    )

        except Exception as ex:#pylint:disable = W0718
            print(F"Backup failed:\nSQL Command:{string}\nException:{ex}")

    @commit_protect_
    def backup(
        self,
        new_table:str,
        *,
        copy_data:bool = True
        ) -> None:

        string = F"SELECT * INTO {new_table} FROM {self.ex_database.table}"
        if not copy_data:
            string += " WHERE 1=0"

        try:
            self.ex_database.cursor.execute(string)

            self.ex_database.history.add_history(
                [
                    self.commit,
                    "new",
                    F"{self.ex_database.host}:"
                    F"{self.ex_database.database}",
                    HistoryAttributes.table,
                    None,
                    new_table
                ]
                )

            if copy_data:
                self.ex_database.cursor.execute(F"SELECT * FROM {new_table}")
                result = pd.DataFrame(self.ex_database.cursor.fetchall())

                for _, row in result.iterrows():
                    self.ex_database.history.add_history(
                        [
                            self.commit,
                            "new",
                            F"{self.ex_database.host}:"
                            F"{self.ex_database.database}."
                            F"{new_table}",
                            HistoryAttributes.column_value,
                            None,
                            row.to_list()
                        ]
                    )

        except Exception as ex:#pylint:disable = W0718
            print(F"Backup failed:\nSQL Command:{string}\nException:{ex}")

    @commit_protect
    async def async_drop(self) -> None:

        sql_string = F"DROP TABLE {self.name}"

        result = await self.select().result
        result = result.data

        try:
            self.ex_database.cursor.execute(sql_string)

            for _,old_row in result.iterrows():
                old_row = old_row.to_list()
                self.ex_database.history.add_history(
                [
                    self.commit,
                    "del",
                    F"{self.ex_database.host}:"
                    F"{self.ex_database.database}.{self.ex_database.table}",
                    HistoryAttributes.column_value,
                    old_row,
                    None
                ]
                )

            self.ex_database.history.add_history(
                [
                    self.commit,
                    "del",
                    F"{self.ex_database.host}:"
                    F"{self.ex_database.database}",
                    HistoryAttributes.table,
                    self.name,
                    None
                ]
                )
        except Exception as ex:#pylint:disable = W0718
            print(F"Drop failed:\nSQL Command:{sql_string}\nException:{ex}")

    @commit_protect_
    def drop(self) -> None:

        sql_string = F"DROP TABLE {self.name}"

        result = self.select().result
        result = result.data

        try:
            self.ex_database.cursor.execute(sql_string)

            for _,old_row in result.iterrows():
                old_row = old_row.to_list()
                self.ex_database.history.add_history(
                [
                    self.commit,
                    "del",
                    F"{self.ex_database.host}:"
                    F"{self.ex_database.database}.{self.ex_database.table}",
                    HistoryAttributes.column_value,
                    old_row,
                    None
                ]
                )

            self.ex_database.history.add_history(
                [
                    self.commit,
                    "del",
                    F"{self.ex_database.host}:"
                    F"{self.ex_database.database}",
                    HistoryAttributes.table,
                    self.name,
                    None
                ]
                )
        except Exception as ex:#pylint:disable = W0718
            print(F"Drop failed:\nSQL Command:{sql_string}\nException:{ex}")

    @commit_protect
    async def async_add_column(
        self,
        column:str,
        datatype:SQLType| str | list[str] | tuple[str],
        ) -> None:

        if isinstance(datatype, (tuple,list)):
            string = F"ALTER TABLE {self.ex_database.table} ADD {column} {' '.join(datatype)}"

        try:
            self.ex_database.cursor.execute(string)
            HistoryControl.add_history(
                self.ex_database.history,
                [
                    self.commit,
                    "new",
                    F"{self.ex_database.host}:"
                    F"{self.ex_database.database}.{self.ex_database.table}",
                    HistoryAttributes.column,
                    None,
                    column
                ]
                )

        except Exception as ex:#pylint:disable = W0718
            print(F"Add field:\nSQL Command:{string}\nException:{ex}")

    @commit_protect_
    def add_column(
        self,
        column:str,
        datatype:SQLType| str | list[str] | tuple[str],
        ) -> None:

        if isinstance(datatype, (tuple,list)):
            string = F"ALTER TABLE {self.ex_database.table} ADD {column} {' '.join(datatype)}"

        try:
            self.ex_database.cursor.execute(string)
            HistoryControl.add_history(
                self.ex_database.history,
                [
                    self.commit,
                    "new",
                    F"{self.ex_database.host}:"
                    F"{self.ex_database.database}.{self.ex_database.table}",
                    HistoryAttributes.column,
                    None,
                    column
                ]
                )

        except Exception as ex:#pylint:disable = W0718
            print(F"Add field:\nSQL Command:{string}\nException:{ex}")

class VTable(ABCVTable):
    """database檢視資料表"""
    def __init__(self, ex_database:EXDataBase) -> None:
        self._ex_database:EXDataBase = ex_database
        self._ex_database._table = ex_database.table
        self._layer = "Table"
        for column in self._columns:
            if column.name in ('ex_database', 'layer', 'commit', 'name'):
                setattr(self,F"{column.name}_",Column(self.ex_database, column))
            else:
                setattr(self,column.name,Column(self.ex_database, column))

    @property
    def ex_database(self) -> EXDataBase:
        """資料庫資訊

        Returns:
            EXDataBase: 資料庫屬性
        """
        return self._ex_database

    @property
    def layer(self) -> str:
        """操作層級"""
        return self._layer

    @property
    def commit(self) -> bool:
        """交易成立設置,當為True時才可成立交易. 預設為False

        Returns:
            bool
        """
        return self._ex_database.commit

    @commit.setter
    def commit(self, _:bool) -> None:
        if not isinstance(_,bool):
            raise TypeError
        self._ex_database.commit = _

    @property
    def name(self) -> str:
        return self.ex_database.table

    @name.setter
    @commit_protect_
    def name(self, _:str) -> None:
        old = self.name
        string = F"EXEC sp_rename '[{self.name}]', '{_}'"
        try:
            self.ex_database.cursor.execute(string)
            self._ex_database._table = _ #pylint:disable=w0212
            self.ex_database.history.add_history(
                [
                    self.commit,
                    "diff",
                    F"{self.ex_database.host}:"
                    F"{self.ex_database.database}",
                    HistoryAttributes.table_name,
                    old,
                    _
                ]
                )
        except Exception as ex:#pylint:disable = W0718
            print(F"Modify field:\nSQL Command:{string}\nException:{ex}")

    @property
    def columns(self) -> tuple[str]:

        return tuple(
            column.name
            if column.name not in ('ex_database', 'layer', 'commit', 'name')
            else F"{column.name}_"
            for column in self._columns
            )

    @property
    def _columns(self) -> tuple[ColumnInfo]:

        self.ex_database.cursor.execute(
            "SELECT COLUMN_NAME,IS_NULLABLE,DATA_TYPE,"
            "CHARACTER_MAXIMUM_LENGTH,NUMERIC_PRECISION, NUMERIC_SCALE,DATETIME_PRECISION"
            F" FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '{self.ex_database.table}'"
        )
        column_list = []
        for table in self._ex_database.cursor.fetchall():

            if table['CHARACTER_MAXIMUM_LENGTH'] is not None:
                length = table['CHARACTER_MAXIMUM_LENGTH']

            elif table['NUMERIC_PRECISION'] and table['NUMERIC_SCALE'] is not None\
            and table['NUMERIC_SCALE'] != 0:
                length = F"{table['NUMERIC_PRECISION']}, {table['NUMERIC_SCALE']}"

            elif table['NUMERIC_PRECISION'] and table['NUMERIC_SCALE'] is not None\
            and table['NUMERIC_SCALE'] == 0:
                length = ""

            elif table['NUMERIC_PRECISION'] is not None and table['NUMERIC_SCALE'] is None:
                length = table['NUMERIC_PRECISION']

            elif table['DATETIME_PRECISION'] is not None:
                length = table['DATETIME_PRECISION']

            else:
                length = ""

            column_list.append(
                ColumnInfo(
                    table['COLUMN_NAME'],
                    F"{table['DATA_TYPE']}({length})",
                    table['IS_NULLABLE']
                )
            )

        return tuple(column_list)

    def select(self, *args, **kwargs) -> _Select:
        return _Select(self.ex_database, *args, **kwargs)
