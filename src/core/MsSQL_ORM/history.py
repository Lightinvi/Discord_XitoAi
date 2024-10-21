#pylint:disable = C0114,C0115,C0116
import re
import os
import ast
import json
import datetime
import threading
from pandas import DataFrame
from rich.console import Console
from rich.table import Table
from rich.style import Style

class HistoryAttributes():

    table = "Table"

    table_name = "TableName"

    column = "Column"

    column_datatype = "ColumnDataType"

    column_name = "ColumnName"

    column_value = "ColumnValue"

class HistoryControl():
    """歷史紀錄控制器"""

    def __init__(self) -> None:
        self.history = None
        self.history_ht = None
        self._lock = threading.Lock()

    def create_history(self, history:str):
        """創建歷史紀錄檔

        Args:
            history (str): 記錄檔名稱
        """
        if not os.path.isdir('history'):
            os.mkdir('history')
        if not os.path.isfile(F"history\\{history}"):
            with open(F"history\\{history}",'w',encoding='utf-8') as create:
                create.write(
                    "[['ID', 'commit', 'status', 'location', 'attributes', 'before', 'after', 'recodeTime'],[]]"#pylint:disable=C0301
                    )
        with open(F"history\\{history}",'r',encoding='utf-8') as history_ht:
            self.history_ht = ast.literal_eval(history_ht.readline())
        self.history = history

    def add_history(self, recode:list[str]) -> list:
        """新增歷史紀錄行

        Args:
            history (str): 記錄檔名稱
            recode (list[str]): 紀錄列表, 列表中需依序輸入
            commit, status, location, attributes, old value, new value

        Returns:
            list: _description_
        """
        with self._lock:
            if self.history_ht[1]:
                recode_id = self.history_ht[1][-1][0] +1
            else:
                recode_id = 0

            recode.append(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            recode = self.row_colorful(recode)
            recode.insert(0,recode_id)
            history_row:list = self.history_ht[1]
            history_row.append(recode)
            self.history_ht[1] = history_row

            with open(F"history\\{self.history}",'w',encoding='utf-8') as history_:
                history_.write(F"{self.history_ht}")

            with open(F"history\\{self.history}",'r',encoding='utf-8') as history_ht:
                self.history_ht = ast.literal_eval(history_ht.readline())

    def row_colorful(self, row:list[str]) -> list[str]:
        """資料行顏色提示

        Args:
            row (list[str]): 原始資料行

        Returns:
            list[str]: 調整後資料行
        """
        match row[0]:
            case True:
                row[0] = F"[green][bold]{row[0]}[/bold][/green]"
            case False:
                row[0] = F"[red][bold]{row[0]}[/bold][/red]"
        match row[1]:
            case "diff":
                for i in range(1,len(row)):
                    row[i] = F"[yellow]{row[i]}[/yellow]"
            case "new":
                for i in range(1,len(row)):
                    row[i] = F"[green]{row[i]}[/green]"
            case "del":
                for i in range(1,len(row)):
                    row[i] = F"[red]{row[i]}[/red]"

        return row

class History():
    @staticmethod
    def read(history_local:str, *,row:int=50,page:int=1) -> None:
        """讀取歷史紀錄檔

        Args:
            history_local (str): 歷史紀錄檔案位置
            row (int, optional): 單頁中讀取行數. Defaults to 100.
            page (int, optional): 頁數. Defaults to 1.
        """
        if "historyTable" not in history_local:
            history_local += ".historyTable"
        with open(history_local,'r',encoding='utf-8') as history_ht:
            history_ht = ast.literal_eval(history_ht.readline())

        history_columns = history_ht[0]
        history_rows = history_ht[1]

        console = Console()
        table = Table(show_header=True, title=history_local)
        table.title_style = Style(color='green', bold=True)

        for column in history_columns:
            table.add_column(column)

        for num, row_data in enumerate(history_rows):
            if num >= (page*row):
                break
            if num < (page*row) - row:
                continue

            row_data = [str(data) for data in row_data]
            row_data = tuple(row_data)

            table.add_row(*row_data)

        console.print(table)

    @staticmethod
    def rollback(ex_database, rollback_df:DataFrame):

        for _, row in rollback_df.iterrows():
            if row['commit'] is False:
                continue

            ex_database.commit = True

            location = row['location'].split(':')[1].split('.')
            match len(location):
                case 0:
                    raise KeyError(F"歷史檔損毀:目前回檔至{_}")
                case 1:
                    database = location[0]
                    table = None
                    column = None
                case 2:
                    database = location[0]
                    table = location[1]
                    column = None
                case 3:
                    database = location[0]
                    table = location[1]
                    column = location[2]

            history_control = HistoryControl()
            history_control.create_history(F"{database}.historyTable")

            match row['attributes']:
                case 'Table':
                    match row['status']:
                        case 'new':
                            ex_database.cursor.execute(
                                F"DROP TABLE {row['after']}"
                            )
                            history_control.add_history(
                                [
                                    True,
                                    "del",
                                    row['location'],
                                    HistoryAttributes.table,
                                    row['after'],
                                    None
                                ]
                            )
                        case 'del':
                            ex_database.cursor.execute(
                                F"CREATE TABLE {row['after']}(temp_SQL_ORM varchar(1))"
                            )
                            history_control.add_history(
                                [
                                    True,
                                    "new",
                                    row['location'],
                                    HistoryAttributes.table,
                                    None,
                                    row['after']
                                ]
                            )

                case 'TableName':
                    ex_database.cursor.execute(
                        F"EXEC sp_rename '[{row['after']}]', '{row['before']}'"
                    )
                    history_control.add_history(
                        [
                            True,
                            "diff",
                            row['location'],
                            HistoryAttributes.table_name,
                            row['after'],
                            row['before']
                        ]
                    )

                case 'Column':
                    match row['status']:
                        case 'new':
                            ex_database.cursor.execute(
                                F"ALTER TABLE {table} DROP COLUMN {row['after']}"
                            )
                            history_control.add_history(
                                [
                                    True,
                                    "del",
                                    row['location'],
                                    HistoryAttributes.column,
                                    row['after'],
                                    None
                                ]
                            )
                        case 'del':
                            pattern = re.compile(r"(\w+)='([^']+)'")
                            matches = pattern.findall(row['before'])
                            column_ = dict(matches)

                            string =\
                                F"ALTER TABLE {table} ADD {column_['name']} {column_['datatype']}"

                            if column_['YES']:
                                string += " NULL"

                            ex_database.cursor.execute(string)

                            history_control.add_history(
                                [
                                    True,
                                    "del",
                                    row['location'],
                                    HistoryAttributes.column,
                                    None,
                                    row['before']
                                ]
                            )

                case 'ColumnDataType':
                    ex_database.cursor.execute(
                        F"ALTER TABLE {table} ALTER COLUMN {column} {row['before']}"
                        )

                    history_control.add_history(
                        [
                            True,
                            "diff",
                            row['location'],
                            HistoryAttributes.column_datatype,
                            row['after'],
                            row['before']
                        ]
                    )

                case 'ColumnValue':
                    match row['status']:
                        case 'new':
                            string = F"DELETE FROM {table}"

                            value_after:dict = json.loads(row['after'])

                            for key,value in value_after.items():
                                if value is None:
                                    value = 'NULL'
                                string += F" {key} = '{value}',"
                            if string[-1] == ',':
                                string = string[:-1]

                            history_control.add_history(
                                [
                                    True,
                                    "del",
                                    row['location'],
                                    HistoryAttributes.column_value,
                                    row['after'],
                                    None
                                ]
                            )
                        case 'del':
                            string = F"INSERT INTO {table} VALUES ("

                            value_before:dict = json.loads(row['before'])

                            for key,value in value_before.items():
                                if value is None:
                                    string += F" {key} = NULL,"
                                else:
                                    string += F" {key} = '{value}',"

                            if string[-1] == ',':
                                string = string[:-1]
                            string += ")"

                            history_control.add_history(
                                [
                                    True,
                                    "new",
                                    row['location'],
                                    HistoryAttributes.column_value,
                                    None,
                                    row['before']
                                ]
                            )
                        case 'diff':
                            string = F"UPDATE {table} SET"

                            value_after:dict = json.loads(row['after'])
                            value_before:dict = json.loads(row['before'])

                            for key,value in value_before.items():
                                if value is None:
                                    string += F" {key} = NULL,"
                                else:
                                    string += F" {key} = '{value}',"

                            if string[-1] == ',':
                                string = string[:-1]

                            string += " WHERE"

                            for key,value in value_after.items():
                                if value is None:
                                    string += F" {key} = NULL,"
                                else:
                                    string += F" {key} = '{value}',"

                            if string[-1] == ',':
                                string = string[:-1]

                            ex_database.cursor.execute(string)
                            history_control.add_history(
                                [
                                    True,
                                    "diff",
                                    row['location'],
                                    HistoryAttributes.column_value,
                                    row['after'],
                                    row['before']
                                ]
                            )

            ex_database.commit = False
