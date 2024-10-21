"""SQL工具 呼叫類別"""
import pymssql
from typing import Union
from .abc import ABCServer,ABCDatabase
from .table import Table,VTable
from .history import HistoryAttributes
from .objects import EXDataBase
from .credentials import DBUser,DBServer

class SQL():
    """建立SQL帳號憑證
    
    Args:
        user (User):帳號物件
    """
    def __init__(self, user:DBUser, *, coding:str = 'utf8') -> None:
        self.user:str = user.account
        self.password:str = user.password
        self._ex_database:EXDataBase = None
        self.coding = coding

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
        return self.ex_database.top_layer

    def connect(self, database:DBServer) -> Union['Database','Server']:
        """連接資料庫

        Args:
            database (DataBase): 資料庫物件

        Returns:
            _SQL: 資料庫類別(已連接)
        """
        ex_database = EXDataBase(pymssql.connect(#pylint: disable = E1101
            host = database.host,
            user = self.user,
            password = self.password,
            database = database.database,
            charset = self.coding
        ),
        database.host,
        database.database
        )

        if database.database is None:
            return Server(self.user, self.password, ex_database, coding = self.coding)
        return Database(self.user, self.password, ex_database, coding = self.coding)

    def disconnect(self) -> None:
        """中斷資料庫連接
        """
        if self.ex_database:
            self.ex_database.cursor.close()
            self.ex_database.db.close()

class Server(ABCServer, SQL):
    """database Server類別"""

    @property
    def databases(self) -> tuple[str]:
        if self.ex_database.database is None:
            self.ex_database.cursor.execute("SELECT name FROM sys.databases where database_id > 4")

            return tuple(database_['name'] for database_ in self.ex_database.cursor.fetchall())
        return None

    async def async_create_database(self, database:str) -> None:
        if self.layer != "Server":
            raise AttributeError("Database操作層級中沒有 method:create_database()")

        sql_string = F"CREATE DATABASE {database}"

        try:
            self.ex_database.db.autocommit(True)
            self.ex_database.cursor.execute(sql_string)
            self.ex_database.db.autocommit(False)

        except Exception as ex:#pylint:disable = W0718
            print(F"Create field:\nSQL Command:{sql_string}\nException:{ex}")

    def create_database(self, database: str) -> None:
        if self.layer != "Server":
            raise AttributeError("Database操作層級中沒有 method:create_database()")

        sql_string = F"CREATE DATABASE {database}"

        try:
            self.ex_database.db.autocommit(True)
            self.ex_database.cursor.execute(sql_string)
            self.ex_database.db.autocommit(False)

        except Exception as ex:#pylint:disable = W0718
            print(F"Create field:\nSQL Command:{sql_string}\nException:{ex}")

    def connect(self, database: DBServer|str = None) -> Union['Server', 'Database']:
        """連接資料庫

        Args:
            database (DataBase): 資料庫物件 或 資料庫名稱

        Returns:
            _SQL: 資料庫類別(已連接)
        """
        self.disconnect()
        if isinstance(database, (str,type(None))):
            return super().connect(DBServer(
                self.ex_database.host,
                database
            ))

        return super().connect(database)

class Database(ABCDatabase, SQL):
    """database類別"""

    @property
    def tables(self) -> tuple[str]:
        if self.ex_database.database is None:
            return None
        self.ex_database.cursor.execute(
            "SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE'"
        )
        return tuple(table['TABLE_NAME'] for table in self._ex_database.cursor.fetchall())

    @property
    def v_tables(self) -> tuple[str]:
        if self.ex_database.database is None:
            return None
        self.ex_database.cursor.execute(
            "SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'VIEW'"
        )
        return tuple(table['TABLE_NAME'] for table in self._ex_database.cursor.fetchall())

    def table(self, tablename: str) -> Table:
        if self.layer != "Database":
            return None

        return Table(
            EXDataBase(
                pymssql.connect(#pylint: disable = E1101
                    host = self.ex_database.host,
                    user = self.user,
                    password = self.password,
                    database =  self.ex_database.database,
                    charset = self.coding
                    ),
                self.ex_database.host,
                self.ex_database.database,
                tablename
                )
            )

    def v_table(self, v_tablename:str) -> VTable:
        if self.layer != "Database":
            return None

        return VTable(
            EXDataBase(
                pymssql.connect(#pylint: disable = E1101
                    host = self.ex_database.host,
                    user = self.user,
                    password = self.password,
                    database =  self.ex_database.database,
                    charset = self.coding
                    ),
                self.ex_database.host,
                self.ex_database.database,
                v_tablename
                )
            )


    async def async_create_table(
            self,
            tablename: str,
            **columns: dict[str, list[str] | tuple[str]] | dict[str, str]
            ) -> None:
        if self.layer != "Database":
            raise AttributeError("Server操作層級中沒有 method:create_table()")

        column_definitions = []
        for column, sql_type in columns.items():
            if isinstance(sql_type, (list, tuple)):
                column_definition = f"{column} {' '.join(sql_type)}"
            else:
                column_definition = f"{column} {sql_type}"
            column_definitions.append(column_definition)

        sql_string = f"CREATE TABLE {tablename} ({', '.join(column_definitions)})"

        try:
            self.ex_database.db.autocommit(True)
            self.ex_database.cursor.execute(sql_string)
            self.ex_database.db.autocommit(False)
            self.ex_database.history.add_history(
                [
                    True,
                    "new",
                    F"{self.ex_database.host}:"
                    F"{self.ex_database.database}",
                    HistoryAttributes.table,
                    None,
                    tablename
                ]
            )

        except Exception as ex:#pylint:disable = W0718
            print(F"Create field:\nSQL Command:{sql_string}\nException:{ex}")

    def create_table(
            self,
            tablename: str,
            **columns: dict[str, list[str] | tuple[str]] | dict[str, str]
            ) -> None:

        if self.layer != "Database":
            raise AttributeError("Server操作層級中沒有 method:create_table()")

        column_definitions = []
        for column, sql_type in columns.items():
            if isinstance(sql_type, (list, tuple)):
                column_definition = f"{column} {' '.join(sql_type)}"
            else:
                column_definition = f"{column} {sql_type}"
            column_definitions.append(column_definition)

        sql_string = f"CREATE TABLE {tablename} ({', '.join(column_definitions)})"

        try:
            self.ex_database.db.autocommit(True)
            self.ex_database.cursor.execute(sql_string)
            self.ex_database.db.autocommit(False)
            self.ex_database.history.add_history(
                [
                    True,
                    "new",
                    F"{self.ex_database.host}:"
                    F"{self.ex_database.database}",
                    HistoryAttributes.table,
                    None,
                    tablename
                ]
            )

        except Exception as ex:#pylint:disable = W0718
            print(F"Create field:\nSQL Command:{sql_string}\nException:{ex}")


    async def async_drop(self) -> None:
        if self.layer != "Server":
            raise AttributeError("Database操作層級中沒有 method:drop_database()")

        sql_string = F"DROP DATABASE {self.ex_database.database}"

        try:
            self.ex_database.db.autocommit(True)
            self.ex_database.cursor.execute(sql_string)
            self.ex_database.db.autocommit(False)

        except Exception as ex:#pylint:disable = W0718
            print(F"Drop field:\nSQL Command:{sql_string}\nException:{ex}")


    def drop(self) -> None:
        if self.layer != "Server":
            raise AttributeError("Database操作層級中沒有 method:drop_database()")

        sql_string = F"DROP DATABASE {self.ex_database.database}"

        try:
            self.ex_database.db.autocommit(True)
            self.ex_database.cursor.execute(sql_string)
            self.ex_database.db.autocommit(False)

        except Exception as ex:#pylint:disable = W0718
            print(F"Drop field:\nSQL Command:{sql_string}\nException:{ex}")

    def connect(self, database: DBServer|str = None) -> Union['Server', 'Database']:
        """連接資料庫

        Args:
            database (DataBase): 資料庫物件 或 資料庫名稱

        Returns:
            _SQL: 資料庫類別(已連接)
        """
        self.disconnect()
        if isinstance(database, (str,type(None))):
            return super().connect(DBServer(
                self.ex_database.host,
                database
            ))

        return super().connect(database)
