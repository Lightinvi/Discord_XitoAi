from abc import ABC, abstractmethod
from typing import Any, Union
from .crud import _Select,_Update,_Insert,_Delete
from .objects import EXDataBase,ColumnInfo
from .checker import commit_protect,commit_protect_
from .sql_type import SQLType
from .credentials import DBUser

class ABCServer(ABC):
    """ABC類別 Server"""
    def __init__(
            self,
            user:str,
            password:str,
            ex_database:EXDataBase,
            *,
            coding: str = 'utf8'
            ) -> None:
        super().__init__(DBUser(user,password), coding=coding)
        self._ex_database = ex_database

        if self._ex_database.database is None:
            self._ex_database._top_layer = "Server"
        else:
            self._ex_database._top_layer = "Database"

    @property
    @abstractmethod
    def databases(self) -> tuple[str]:
        """查看伺服器中有那些資料庫(如果已連接資料庫則回傳None)

        Returns:
            tuple[str]: 資料庫列表
        """

    @abstractmethod
    async def async_create_database(self, database:str) -> None:
        """創建資料庫(異步)(注意!此方法不受保護機制控制(commit,history))

        Args:
            database (str): 資料庫名稱

        """

    @abstractmethod
    def create_database(self, database:str) -> None:
        """創建資料庫(注意!此方法不受保護機制控制(commit,history))

        Args:
            database (str): 資料庫名稱

        """

class ABCDatabase(ABC):
    """ABC類別 Database"""
    def __init__(
            self,
            user:str,
            password:str,
            ex_database:EXDataBase,
            *,
            coding: str = 'utf8'
            ) -> None:
        super().__init__(DBUser(user,password), coding=coding)
        self._ex_database = ex_database

        if self._ex_database.database is None:
            self._ex_database._top_layer = "Server"
        else:
            self._ex_database._top_layer = "Database"

    @property
    @abstractmethod
    def tables(self) -> tuple[str]:
        """查看資料庫中有那些資料表(如果未連接資料庫則回傳None)

        Returns:
            tuple[str]: 資料表名稱
        """

    @property
    @abstractmethod
    def v_tables(self) -> tuple[str]:
        """查看資料庫中有那些檢視資料表(如果未連接資料庫則回傳None)

        Returns:
            tuple[str]: 檢視資料表名稱
        """

    @abstractmethod
    def table(self, tablename:str) -> 'ABCTable':
        """連接操作資料表

        Args:
            tablename (str): 資料表名稱

        Returns:
            Table: 資料表類別

        Notice:
            當資料表欄位中有以下關鍵字'ex_database', 'layer', 'commit', 'name'
            呼叫欄位時後方需加 '_'
        """

    @abstractmethod
    def v_table(self, v_tablename:str) -> 'ABCVTable':
        """連接檢視資料表

        Args:
            tablename (str): 資料表名稱

        Returns:
            Table: 資料表類別

        Notice:
            當資料表欄位中有以下關鍵字'ex_database', 'layer', 'commit', 'name'
            呼叫欄位時後方需加 '_'
        """

    @abstractmethod
    async def async_create_table(
        self,
        tablename:str,
        **columns:Union[dict[str,Union[list[str],tuple[str]]],dict[str,str]]
    ) -> None:
        """創建資料表(異步)(注意!此方法不受保護機制控制(commit))

        Args:
            tablename (str): 資料表名稱
            **columns: ex -> 欄位名稱 = 資料型態

            資料型態可附加條件
            - PRIMARY KEY : 設定成主索引鍵
            - NOT NULL : 禁止欄位為空
            - UNIQUE : 禁止資料重複

        """

    @abstractmethod
    def create_table(
        self,
        tablename:str,
        **columns:Union[dict[str,Union[list[str],tuple[str]]],dict[str,str]]
    ) -> None:
        """創建資料表(注意!此方法不受保護機制控制(commit))

        Args:
            tablename (str): 資料表名稱
            **columns: ex -> 欄位名稱 = 資料型態

            資料型態可附加條件
            - PRIMARY KEY : 設定成主索引鍵
            - NOT NULL : 禁止欄位為空
            - UNIQUE : 禁止資料重複

        """

    @abstractmethod
    async def async_drop(self) -> None:
        """刪除當前資料庫(異步)(注意!此方法不受保護機制控制(commit,history))
        """

    @abstractmethod
    def drop(self) -> None:
        """刪除當前資料庫(注意!此方法不受保護機制控制(commit,history))
        """

class ABCTable(ABC):
    """ABC類別 Table"""

    @property
    @abstractmethod
    def ex_database(self) -> EXDataBase:
        """資料庫資訊(commit屬性可在此設定)

        Returns:
            EXDataBase: 資料庫屬性
        """

    @property
    @abstractmethod
    def commit(self) -> bool:
        """交易成立設置,當為True時才可成立交易. 預設為False

        Returns:
            bool
        """

    @commit.setter
    @abstractmethod
    def commit(self, _:bool) -> None:
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """資料表名稱"""

    @name.setter
    @commit_protect_
    @abstractmethod
    def name(self, _:str) -> None:
        pass

    @property
    @abstractmethod
    def columns(self) -> tuple[ColumnInfo]:
        """資料表中的所有欄位

        Returns:
            tuple[Column]: 欄位名稱和資料型態
        """

    @abstractmethod
    def select(self, *args, **kwargs) -> _Select:
        """資料表 搜尋資料

        Args:
            distinct (bool): 單一搜尋

        Returns:
            _Select: Select操作類別
        """

    @abstractmethod
    def update(self, **columns:Any) -> _Update:
        """資料表更新 (不支援更新整張表)

        Returns:
            _Update: Update操作類別
        """

    @abstractmethod
    def insert(self, *columns:Any) -> _Insert:
        """資料表 新增資料

        Args:
            columns (tuple[_Column]): 新增欄位,若無則預設所有欄位

        Returns:
            _Insert: Insert操作類別
        """

    @abstractmethod
    def delete(self, quantity) -> _Delete:
        """資料表 刪除資料(不支援所有資料刪除,若需要刪除所有資料請使用truncate)

        Returns:
            _Delete: Delete操作類別
        """

    @commit_protect
    @abstractmethod
    async def async_truncate(self) -> None:
        """資料表 刪除所有資料(異步)

        """

    @commit_protect_
    @abstractmethod
    def truncate(self) -> None:
        """資料表 刪除所有資料

        """

    @commit_protect
    @abstractmethod
    async def async_backup(
        self,
        new_table:str,
        *,
        copy_data:bool = True,
        ) -> None:
        """備份當前資料表(異步)

        Args:
            new_table (str): 複製後的資料表名稱
            copy_data (bool, optional): 是否複製內容資料. Defaults to True.
            goto (bool, optional): 複製後是否直接使用該表. Defaults to False.
        """

    @commit_protect_
    @abstractmethod
    def backup(
        self,
        new_table:str,
        *,
        copy_data:bool = True,
        ) -> None:
        """備份當前資料表

        Args:
            new_table (str): 複製後的資料表名稱
            copy_data (bool, optional): 是否複製內容資料. Defaults to True.
            goto (bool, optional): 複製後是否直接使用該表. Defaults to False.
        """

    @commit_protect
    @abstractmethod
    async def async_drop(self) -> None:
        """刪除資料表(異步)
        """

    @commit_protect_
    @abstractmethod
    def drop(self) -> None:
        """刪除資料表
        """

    @commit_protect
    @abstractmethod
    async def async_add_column(
        self,
        column:str,
        datatype:SQLType| str | list[str] | tuple[str]
        ) -> None:
        """新增欄位(異步)

        Args:
            column (str): 欄位名稱
            datatype (SQLType): 資料型態

        資料型態可附加條件
            - PRIMARY KEY : 設定成主索引鍵
            - NOT NULL : 禁止欄位為空
            - UNIQUE : 禁止資料重複
        """

    @commit_protect_
    @abstractmethod
    def add_column(
        self,
        column:str,
        datatype:SQLType| str | list[str] | tuple[str]
        ) -> None:
        """新增欄位

        Args:
            column (str): 欄位名稱
            datatype (SQLType): 資料型態

        資料型態可附加條件
            - PRIMARY KEY : 設定成主索引鍵
            - NOT NULL : 禁止欄位為空
            - UNIQUE : 禁止資料重複
        """

class ABCVTable(ABC):
    """ABC類別Vtable"""
    @property
    @abstractmethod
    def ex_database(self) -> EXDataBase:
        """資料庫資訊(commit屬性可在此設定)

        Returns:
            EXDataBase: 資料庫屬性
        """

    @property
    @abstractmethod
    def commit(self) -> bool:
        """交易成立設置,當為True時才可成立交易. 預設為False

        Returns:
            bool
        """

    @commit.setter
    @abstractmethod
    def commit(self, _:bool) -> None:
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """檢視資料表名稱"""

    @name.setter
    @commit_protect_
    @abstractmethod
    def name(self, _:str) -> None:
        pass

    @property
    @abstractmethod
    def columns(self) -> tuple[ColumnInfo]:
        """資料表中的所有欄位

        Returns:
            tuple[Column]: 欄位名稱和資料型態
        """

    @abstractmethod
    def select(self, *args, **kwargs) -> _Select:
        """資料表 搜尋資料

        Args:
            distinct (bool): 單一搜尋

        Returns:
            _Select: Select操作類別
        """

class ABCColumn(ABC):
    """ABC類別 Column"""
    @property
    @abstractmethod
    def datatype(self) -> str:
        """資料型態"""

    @datatype.setter
    @commit_protect_
    @abstractmethod
    def datatype(self, _type:SQLType) -> None:
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """欄位名稱"""

    @name.setter
    @commit_protect_
    @abstractmethod
    def name(self, _:str):
        pass

    @property
    def nullable(self) -> bool:
        """可否為空"""

    @nullable.setter
    @commit_protect_
    def nullable(self, _:bool) -> None:
        pass

    @commit_protect
    @abstractmethod
    async def async_drop(self) -> None:
        """刪除欄位(異步)
        """

    @commit_protect_
    @abstractmethod
    def drop(self) -> None:
        """刪除欄位
        """
