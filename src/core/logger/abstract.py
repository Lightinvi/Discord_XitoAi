from abc import ABC, abstractmethod

class ISetting(ABC):
    """<Abstract>Logger Setting"""

    @property
    @abstractmethod
    def encoding(self) -> str:
        """Logger當前編碼
        """

    @encoding.setter
    @abstractmethod
    def encoding(self, new_conding:str) -> str:
        pass

    @property
    @abstractmethod
    def level(self) -> str:
        """Logger紀錄等級
        """

    @level.setter
    @abstractmethod
    def level(self, new_level:str) -> str:
        pass

    @property
    @abstractmethod
    def location(self) -> str:
        """Logger當前存儲位置
        """

    @location.setter
    @abstractmethod
    def location(self, new_location) -> str:
        pass


class IWrite(ABC):
    """<Abstract>Logger Write"""

    @abstractmethod
    def debug(self, message:str, *, output:bool = False):
        """紀錄Debug等級的訊息

        Args:
            message (str): 訊息內容
            output (bool): 是否打印至終端機
        """

    @abstractmethod
    def info(self, message:str, *, output:bool = False):
        """紀錄Info等級的訊息

        Args:
            message (str): 訊息內容
            output (bool): 是否打印至終端機
        """

    @abstractmethod
    def warning(self, message:str, *, output:bool = False):
        """紀錄Warning等級的訊息

        Args:
            message (str): 訊息內容
            output (bool): 是否打印至終端機
        """

    @abstractmethod
    def error(self, message:str, *, output:bool = False):
        """紀錄Error等級的訊息

        Args:
            message (str): 訊息內容
            output (bool): 是否打印至終端機
        """

    @abstractmethod
    def critical(self, message:str, *, output:bool = False):
        """紀錄Critical等級的訊息

        Args:
            message (str): 訊息內容
            output (bool): 是否打印至終端機
        """

class ILoggerUI(ABC):
    """<Abstract>Logger 主操作"""

    @property
    @abstractmethod
    def setting(self) -> ISetting:
        """設定Logger
        """

    @property
    @abstractmethod
    def write(self) -> IWrite:
        """寫入Logger
        """
