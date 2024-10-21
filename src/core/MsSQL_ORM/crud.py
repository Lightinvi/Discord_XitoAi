"""CRUD"""
from typing import Self,Any,Union
import copy
import pandas as pd

from .checker import commit_protect, commit_protect_
from .objects import EXDataBase,_Extend,QueryResult,Operation
from .history import HistoryAttributes

class _Select(_Extend):
    def __init__(self, ex_database: EXDataBase, *args, **kwargs) -> None:
        super().__init__(ex_database)
        self._sql_string = "SELECT"

        if kwargs.get('distinct', False):
            if not isinstance(kwargs['distinct'], bool):
                raise TypeError("distinct 應為 True or False")

            self._sql_string = "SELECT DISTINCT"

        if args:
            temp_string = ",".join(args)
        else:
            temp_string = "*"

        self._sql_string += F" {temp_string} FROM [{self.ex_database.table}]"

    def __repr__(self) -> str:
        return "請使用 result 獲取搜尋結果"

    @property
    async def async_result(self) -> QueryResult | None:
        """搜尋結果

        Returns:
            QueryResult | None: 選擇資料呈現方式
        """

        try:
            self._ex_database.cursor.execute(self._sql_string)

            return QueryResult(self._ex_database.cursor.fetchall(), self.ex_database.table)
        except Exception as ex: #pylint:disable = W0718
            return print(F"Result failed:\nSQL Command:{self._sql_string}\nException:{ex}")

    @property
    def result(self) -> QueryResult | None:
        """搜尋結果

        Returns:
            QueryResult | None: 選擇資料呈現方式
        """

        try:
            self._ex_database.cursor.execute(self._sql_string)

            return QueryResult(self._ex_database.cursor.fetchall(), self.ex_database.table)
        except Exception as ex: #pylint:disable = W0718
            return print(F"Result failed:\nSQL Command:{self._sql_string}\nException:{ex}")

    def where(self, condition:Operation) -> Self:
        """依照條件搜尋

        Args:
            condition (Condition): 搜尋條件

        Raises:
            ValueError

        Returns:
            _Select
        """
        if not condition:
            raise ValueError("未輸入條件")

        self._sql_string += " WHERE"

        self._sql_string += F" {condition.sql_string}"

        return self

    def order_by(self, *columns:str) -> Self:
        """依照指定欄位排序

        Args:
            columns (str):欄位

        Raises:
            ValueError

        Returns:
            _Select
        """
        if not columns:
            raise ValueError("未輸入欄位")

        columns = ",".join(columns)
        self._sql_string += F" ORDER BY {columns}"

        return self

    def group_by(self, *columns:str) -> Self:
        """依照欄位分組

        Args:
            columns (str):欄位

        Raises:
            ValueError

        Returns:
            _Select
        """
        if not columns:
            raise ValueError("未輸入欄位")

        columns = ",".join(columns)
        self._sql_string += F" GROUP BY {columns}"

        return self

    def join( #pylint:disable = R0913
            self,
            mode:str,
            table:str,
            condition:Operation
            ) -> '_Select':
        """將資料表鍵入

        Args:
            mode (str): 鍵入模式('LEFT', 'RIGHT', 'INNER', 'FULL')
            table (str): 鍵入資料表
            condition (Operation): 鍵入條件

        Raises:
            ValueError

        Returns:
            _Select
        """
        mode_list = ('LEFT', 'RIGHT', 'INNER', 'FULL')

        mode = mode.upper()

        if mode not in mode_list:
            raise ValueError("鍵入模式錯誤")

        if not condition:
            raise ValueError("未輸入條件")

        self._sql_string += F" {mode} JOIN {table} ON"

        self._sql_string += F" {condition.sql_string}"

        return self

class _Update(_Extend):
    def __init__(self, ex_database: EXDataBase, **columns:Any) -> None:
        super().__init__(ex_database)

        if not columns:
            raise ValueError("未輸入欄位")

        self.columns = columns

        self.sql_string = F"UPDATE [{self.ex_database.table}] SET"

        for column, value in columns.items():
            if value is None:
                self.sql_string += F" {column} = NULL,"
            elif str(value)[0] == '*' or str(value)[0] == 'N':
                self.sql_string += F" {column} = {str(value)[1:]},"
            else:
                self.sql_string += F" {column} = '{value}',"

        if self.sql_string[-1] == ',':
            self.sql_string = self.sql_string[:-1]

    def __repr__(self) -> str:
        return "請使用 where() 設定更新條件"

    @commit_protect
    async def async_where(self, condition:Operation) -> bool:
        """資料表更新 更新位置條件

        Args:
            condition (Operation): 欄位條件

        """

        if not condition:
            raise ValueError("未輸入條件")

        self.ex_database.cursor.execute(
            F"SELECT * FROM {self.ex_database.table} WHERE {condition}"
            )
        old_data = pd.DataFrame(self.ex_database.cursor.fetchall())

        self.sql_string += F" WHERE {condition}"

        try:
            self.ex_database.cursor.execute(self.sql_string)

            for _,old_row in old_data.iterrows():
                old_row = old_row.to_dict()
                new_row = copy.deepcopy(old_row)
                for column, value in self.columns.items():
                    new_row[column] = value
                self.ex_database.history.add_history(
                [
                    self.commit,
                    "diff",
                    F"{self.ex_database.host}:"
                    F"{self.ex_database.database}.{self.ex_database.table}",
                    HistoryAttributes.column_value,
                    old_row,
                    new_row
                ]
                )
            return True
        except Exception as ex:#pylint:disable = W0718
            print(F"Update failed:\nSQL Command:{self.sql_string}\nException:{ex}")
            return False

    @commit_protect_
    def where(self, condition:Operation) -> None:
        """資料表更新 更新位置條件

        Args:
            condition (Operation): 欄位條件

        """

        if not condition:
            raise ValueError("未輸入條件")

        self.ex_database.cursor.execute(
            F"SELECT * FROM [{self.ex_database.table}] WHERE {condition}"
            )
        old_data = pd.DataFrame(self.ex_database.cursor.fetchall())

        self.sql_string += F" WHERE {condition}"

        try:
            self.ex_database.cursor.execute(self.sql_string)

            for _,old_row in old_data.iterrows():
                old_row = old_row.to_dict()
                new_row = copy.deepcopy(old_row)
                for column, value in self.columns.items():
                    new_row[column] = value
                self.ex_database.history.add_history(
                [
                    self.commit,
                    "diff",
                    F"{self.ex_database.host}:"
                    F"{self.ex_database.database}.{self.ex_database.table}",
                    HistoryAttributes.column_value,
                    old_row,
                    new_row
                ]
                )

        except Exception as ex:#pylint:disable = W0718
            print(F"Update failed:\nSQL Command:{self.sql_string}\nException:{ex}")

class _Insert(_Extend):
    def __init__(self, ex_database: EXDataBase, *columns:Any) -> None:
        super().__init__(ex_database)

        if columns:
            self.columns = [column.__str__() for column in columns]
            self.sql_string = F"INSERT INTO [{self.ex_database.table}] ({','.join(self.columns)})"
        else:
            self.sql_string = F"INSERT INTO [{self.ex_database.table}]"

    def __repr__(self) -> str:
        return "使用 values() 填入新增資料"

    def __str__(self) -> str:
        return "使用 values() 填入新增資料"

    @commit_protect
    async def async_values(self, *data: Union[Any, list[Any], tuple[Any]]) -> None:
        """新增資料內容

        Args:
            data (Any, list[Any], tuple[Any]): 使用 list 或 tuple 將會判定每個list、tuple為一筆資料
                若輸入方式不是list或tuple而是str,int,etc...則所有輸入判定為一筆資料

        Raises:
            ValueError: 輸入資料格式不統一

        """

        if isinstance(data[0],(list,tuple)):
            check_list = (list,tuple)
            mode = 'multiple'
        else:
            check_list = (str,int,float,bool,type(None))
            mode = 'single'
        if not all(isinstance(item, check_list) for item in data):
            raise ValueError("請檢查新增資料的一致性")

        match mode:
            case 'single':
                values = ','.join(
                    ["NULL" if value is None else F"'{value}'"
                    if str(value)[0] != '*' or str(value)[0] != 'N' else str(value)[1:]
                    for value in data]
                )
                self.sql_string += F" VALUES ({values})"

            case 'multiple':
                self.sql_string += " VALUES"
                temp:list = []

                for value_data in data:
                    values = ','.join(
                        ["NULL" if value is None else F"'{value}'"
                        if str(value)[0] != '*' or str(value)[0] != 'N' else str(value)[1:]
                        for value in value_data]
                    )
                    temp.append(F"({values})")

                self.sql_string += F" {','.join(temp)}"

        try:
            self.ex_database.cursor.execute(F"SELECT * FROM {self.ex_database.table}")
            old_data = pd.DataFrame(self.ex_database.cursor.fetchall())

            self._ex_database.cursor.execute(self.sql_string)

            self.ex_database.cursor.execute(F"SELECT * FROM {self.ex_database.table}")
            new_data = pd.DataFrame(self.ex_database.cursor.fetchall())

            diff_data = pd.concat([new_data,old_data,old_data]).drop_duplicates(keep=False)

            for _,row in diff_data.iterrows():
                self.ex_database.history.add_history(
                    [
                        self.commit,
                        "new",
                        F"{self.ex_database.host}:"
                        F"{self.ex_database.database}.{self.ex_database.table}",
                        HistoryAttributes.column_value,
                        None,
                        row.to_dict()
                    ]
                    )

        except Exception as ex:#pylint:disable = W0718
            print(F"Insert failed:\nSQL Command:{self.sql_string}\nException:{ex}")

    @commit_protect_
    def values(self, *data: Union[Any, list[Any], tuple[Any]]) -> None:
        """新增資料內容

        Args:
            data (Any, list[Any], tuple[Any]): 使用 list 或 tuple 將會判定每個list、tuple為一筆資料
                若輸入方式不是list或tuple而是str,int,etc...則所有輸入判定為一筆資料

        Raises:
            ValueError: 輸入資料格式不統一

        """

        if isinstance(data[0],(list,tuple)):
            check_list = (list,tuple)
            mode = 'multiple'
        else:
            check_list = (str,int,float,bool,type(None))
            mode = 'single'
        if not all(isinstance(item, check_list) for item in data):
            raise ValueError("請檢查新增資料的一致性")

        match mode:
            case 'single':
                values = ','.join(
                    ["NULL" if value is None else F"'{value}'"
                    if str(value)[0] != '*' or str(value)[0] != 'N' else str(value)[1:]
                    for value in data]
                )
                self.sql_string += F" VALUES ({values})"

            case 'multiple':
                self.sql_string += " VALUES"
                temp:list = []

                for value_data in data:
                    values = ','.join(
                        ["NULL" if value is None else F"'{value}'"
                        if str(value)[0] != '*' or str(value)[0] != 'N' else str(value)[1:]
                        for value in value_data]
                    )
                    temp.append(F"({values})")

                self.sql_string += F" {','.join(temp)}"

        try:
            self.ex_database.cursor.execute(F"SELECT * FROM [{self.ex_database.table}]")
            old_data = pd.DataFrame(self.ex_database.cursor.fetchall())

            self._ex_database.cursor.execute(self.sql_string)

            self.ex_database.cursor.execute(F"SELECT * FROM [{self.ex_database.table}]")
            new_data = pd.DataFrame(self.ex_database.cursor.fetchall())

            diff_data = pd.concat([new_data,old_data,old_data]).drop_duplicates(keep=False)

            for _,row in diff_data.iterrows():
                self.ex_database.history.add_history(
                    [
                        self.commit,
                        "new",
                        F"{self.ex_database.host}:"
                        F"{self.ex_database.database}.{self.ex_database.table}",
                        HistoryAttributes.column_value,
                        None,
                        row.to_dict()
                    ]
                    )

        except Exception as ex:#pylint:disable = W0718
            print(F"Insert failed:\nSQL Command:{self.sql_string}\nException:{ex}")

class _Delete(_Extend):
    def __init__(self, ex_database: EXDataBase, quantity:int) -> None:
        super().__init__(ex_database)
        self.quantity = quantity

    @commit_protect
    async def async_where(self, condition:Operation) -> None:
        """資料表刪除 刪除位置條件

        Args:
            condition (Operation): 欄位條件

        Raises:
            ValueError: 未輸入欄位條件

        """
        if not condition:
            raise ValueError("未輸入欄位")

        if self.quantity == -1:
            select_string = F"SELECT * FROM {self.ex_database.table} WHERE {condition}"
            del_string = F"DELETE FROM {self.ex_database.table}"
        else:
            select_string =\
                F"SELECT TOP({self.quantity}) * FROM {self.ex_database.table} WHERE {condition}"
            del_string = F"DELETE TOP({self.quantity}) FROM {self.ex_database.table}"

        self.ex_database.cursor.execute(select_string)

        old_data = pd.DataFrame(self.ex_database.cursor.fetchall())

        del_string += F" WHERE {condition}"

        try:
            self._ex_database.cursor.execute(del_string)

            for _,old_row in old_data.iterrows():

                self.ex_database.history.add_history(
                [
                    self.commit,
                    "del",
                    F"{self.ex_database.host}:"
                    F"{self.ex_database.database}.{self.ex_database.table}",
                    HistoryAttributes.column_value,
                    old_row.to_dict(),
                    None
                ]
                )

        except Exception as ex:#pylint:disable = W0718
            print(F"Delete failed:\nSQL Command:{del_string}\nException:{ex}")

    @commit_protect_
    def where(self, condition:Operation) -> None:
        """資料表刪除 刪除位置條件

        Args:
            condition (Operation): 欄位條件

        Raises:
            ValueError: 未輸入欄位條件

        """
        if not condition:
            raise ValueError("未輸入欄位")

        if self.quantity == -1:
            select_string = F"SELECT * FROM {self.ex_database.table} WHERE {condition}"
            del_string = F"DELETE FROM {self.ex_database.table}"
        else:
            select_string =\
                F"SELECT TOP({self.quantity}) * FROM {self.ex_database.table} WHERE {condition}"
            del_string = F"DELETE TOP({self.quantity}) FROM {self.ex_database.table}"

        self.ex_database.cursor.execute(select_string)

        old_data = pd.DataFrame(self.ex_database.cursor.fetchall())

        del_string += F" WHERE {condition}"

        try:
            self._ex_database.cursor.execute(del_string)

            for _,old_row in old_data.iterrows():

                self.ex_database.history.add_history(
                [
                    self.commit,
                    "del",
                    F"{self.ex_database.host}:"
                    F"{self.ex_database.database}.{self.ex_database.table}",
                    HistoryAttributes.column_value,
                    old_row.to_dict(),
                    None
                ]
                )

        except Exception as ex:#pylint:disable = W0718
            print(F"Delete failed:\nSQL Command:{del_string}\nException:{ex}")

