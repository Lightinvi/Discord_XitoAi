#pylint:disable=C0114
from abc import ABC,abstractmethod
import discord

class IFakeInteraction(ABC):
    """<Interface> 偽裝用戶或公會使其可被資料庫讀取"""

    @property
    @abstractmethod
    def user(self) -> discord.User:
        """用戶資訊"""

    @property
    @abstractmethod
    def guild(self) -> discord.Guild:
        """公會資訊"""

class IDisocrdEntityInfo(ABC):
    """<Interface> discord實體物件(user,guild)的資訊獲取與更新"""

    @abstractmethod
    def _db_get(self) -> None:
        """從資料庫獲取實體資訊"""

    @abstractmethod
    def db_update(self) -> None:
        """將變更更新至資料庫"""

    @abstractmethod
    def _db_create(self) -> None:
        """於資料庫創建實體資訊"""

    @property
    @abstractmethod
    def id(self) -> str:
        """實體資訊ID"""

    @property
    @abstractmethod
    def name(self) -> str:
        """實體資訊名稱"""

    @property
    @abstractmethod
    def sync(self) -> bool:
        """是否請求同步

        Returns:
            bool: 當為True時,代表需要透過 db_update 來更新資料庫
        """
