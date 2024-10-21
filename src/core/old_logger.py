"""Logs紀錄器"""

import datetime
import logging
from functools import wraps
from rich import print as c_print

class Logger():
    """Logger套件"""
    class _Setting():
        """Logger._Setting 設定細節"""

        def __init__(self) -> None:
            self._encode = 'utf-8'
            self._log_level = logging.INFO
            self._log_location = F"logs\\{datetime.datetime.today().strftime('%Y-%m-%d')}.log"

        def init_setting(self) -> None:
            """初始化設定值
            """
            self._encode = 'utf-8'
            self._log_level = logging.INFO
            self._log_location = F"logs\\{datetime.datetime.today().strftime('%Y-%m-%d')}.log"

        @property
        def encode(self) -> str:
            """編碼變數

            Returns:
                str: 當前設置的編碼
            """
            return self._encode

        @encode.setter
        def encode(self, encode) -> None:
            self._encode = encode

        @property
        def log_level(self) -> int:
            """log等級變數

            Returns:
                int: 當前log等級int參數
            """
            return self._log_level

        @log_level.setter
        def log_level(self, level:str) -> None:
            level = level.upper()

            match level:
                case "DEBUG": self._log_level = logging.DEBUG

                case "INFO": self._log_level = logging.INFO

                case "WARRING": self._log_level = logging.WARNING

                case "ERROR": self._log_level = logging.ERROR

                case "CRITICAL": self._log_level = logging.CRITICAL

                case _: raise ValueError("請選擇輸入以下規範參數\nDEBUG\\INFO\\WARRING\\ERROR\\CRITICAL")

        @property
        def log_location(self) -> str:
            """儲存位置變數

            Returns:
                str: 當前設置的儲存位置
            """
            return self._log_location

        @log_location.setter
        def log_location(self, location) -> None:
            self._log_location = \
                F"{location}\\{datetime.datetime.today().strftime('%Y-%m-%d')}.log"


    class _Level():
        """寫入時等級選擇
        """
        @staticmethod
        def debug(message:str, print_out:bool = False) -> None:
            """選項-Debug

            Args:
                message (str): 紀錄訊息
            """
            logging.debug(message, exc_info=None)
            if print_out is True:
                time = datetime.datetime.today().strftime('[%Y/%m/%d|%H:%M:%S]')
                c_print(F"{time}[[magenta]DEBUG[/magenta]]:{message}")

        @staticmethod
        def info(message:str, print_out:bool = False) -> None:
            """選項-Info

            Args:
                message (str): 紀錄訊息
            """
            logging.info(message, exc_info=None)
            if print_out is True:
                time = datetime.datetime.today().strftime('[%Y/%m/%d|%H:%M:%S]')
                c_print(F"{time}[[green]INFO[/green]]:{message}")

        @staticmethod
        def warning(message:str, print_out:bool = False) -> None:
            """選項-Warning

            Args:
                message (str): 紀錄訊息
            """
            logging.warning(message, exc_info=None)
            if print_out is True:
                time = datetime.datetime.today().strftime('[%Y/%m/%d|%H:%M:%S]')
                c_print(F"{time}[[yellow]WARNING[/yellow]]:{message}")

        @staticmethod
        def error(message:str, print_out:bool = False) -> None:
            """選項-Error

            Args:
                message (str): 紀錄訊息
            """
            logging.error(message, exc_info=True)
            if print_out is True:
                time = datetime.datetime.today().strftime('[%Y/%m/%d|%H:%M:%S]')
                c_print(F"{time}[[red]ERROR[/red]]:{message}")

        @staticmethod
        def critical(message:str, print_out:bool = False) -> None:
            """選項-Critical

            Args:
                message (str): 紀錄訊息
            """
            logging.error(message, exc_info=True)
            if print_out is True:
                time = datetime.datetime.today().strftime('[%Y/%m/%d|%H:%M:%S]')
                c_print(F"{time}[[red bold]CRITICAL[/red bold]]:{message}")

    _setting = _Setting()

    @classmethod
    def setting(cls, location:str=None, level:str=None, encode:str=None) -> None:
        """調整紀錄設定

        Args:
            location (str, optional): 儲存位置. Defaults to None.\n
            level (str, optional): 紀錄等級. Defaults to None.\n
            encode (str, optional): 紀錄文件編碼. Defaults to None.\n
        """
        cls._setting.encode = encode or "UTF-8"

        cls._setting.log_level = level or "INFO"

        cls._setting.log_location = location or "logs"

    @classmethod
    def write(cls, location:str=None, level:str=None, encode:str=None) -> _Level:
        """手動寫入紀錄文檔

        Args:
            location (str, optional): 儲存位置. Defaults to None.\n
            level (str, optional): 紀錄等級. Defaults to None.\n
            encode (str, optional): 紀錄文件編碼. Defaults to None.\n

        Returns:
            _Level: 選擇紀錄等級
        """
        cls.setting(location, encode, level)

        logging.basicConfig(
            filename=cls._setting.log_location,
            encoding=cls._setting.encode,
            level=cls._setting.log_level,
            datefmt='%Y/%m/%d|%H:%M:%S',
            format='[%(asctime)s][%(levelname)s]:%(message)s'
        )

        return cls._Level

class LoggerDecorator:
    """log紀錄裝飾器"""
    @staticmethod
    def before_action(message:str=None):
        """於執行動作前寫入log"""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                if message is None:
                    output_message = func.__name__
                else:
                    output_message = message
                Logger.write().info(F"開始執行->{output_message}")
                call_func = func(*args, **kwargs)
                return call_func
            return wrapper
        return decorator

    @staticmethod
    def after_action(message:str=None):
        """於執行動作後寫入log"""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                if message is None:
                    output_message = func.__name__
                else:
                    output_message = message
                call_func = func(*args, **kwargs)
                Logger.write().info(F"結束執行->{output_message}")
                return call_func
            return wrapper
        return decorator

    @staticmethod
    def before_after_action(message:str=None):
        """於執行動作前後寫入log"""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                if message is None:
                    output_message = func.__name__
                else:
                    output_message = message
                Logger.write().info(F"開始執行->{output_message}")
                call_func = func(*args, **kwargs)
                Logger.write().info(F"結束執行->{output_message}")
                return call_func
            return wrapper
        return decorator

    @staticmethod
    def func_reporter(func):
        """function checker

        Args:
            func (Any): Use modifiers before functions

        Returns:
            Any: If no error occurs in the function, return function, otherwise return None
        """
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as ex:# pylint: disable=broad-except

                class_name = args[0].__class__.__name__
                if class_name == "str":
                    class_name = "__main__"

                error_string = \
                    F"A/An {ex.__class__.__name__} occurred in {class_name}.{func.__name__}"
                Logger.write().error(error_string)

                return None

        return wrapper

    @staticmethod
    def async_func_reporter(func):
        """function checker

        Args:
            func (Any): Use modifiers before functions

        Returns:
            Any: If no error occurs in the function, return function, otherwise return None
        """
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await func(*args, **kwargs)
            except Exception as ex:# pylint: disable=broad-except

                class_name = args[0].__class__.__name__
                if class_name == "str":
                    class_name = "__main__"

                error_string = \
                    F"A/An {ex.__class__.__name__} occurred in {class_name}.{func.__name__}"
                Logger.write().error(error_string)

                return None

        return wrapper
