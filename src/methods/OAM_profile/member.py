# pylint: disable= C0114,E1101,R0902
import discord
from src.core import SQL,db_account,db_server,SQLConvert,Logger

from .user import DiscordUser
from .guild import DiscordGuild
from .interface import IDisocrdEntityInfo

INFOTABLE = "memberInfo"
STARTABLE = "memberStar"
ONLINETABLE = "memberOnline"

logger = Logger()

class ExMember():
    """例外/擴展資料庫資訊"""
    result:dict = {}
    result.setdefault("star",(1,0))
    result.setdefault("online_time",('2019-12-25', 0, False))

    @classmethod
    def get(cls, uid:str) -> dict:
        """獲取例外的資料庫資訊"""
        ex = tuple(
                method
                for method in dir(cls.Get)
                if callable(getattr(cls.Get, method)) and
                not method.startswith('__') and
                not method.startswith('_')
            )

        for method_name in ex:
            method = getattr(cls.Get, method_name)
            cls.result[method_name] = method(uid)

        return cls.result

    @classmethod
    def create(cls, uid:str) -> None:
        """資料庫創建擴增資訊"""
        ex = tuple(
                method
                for method in dir(cls.Create)
                if callable(getattr(cls.Create, method)) and
                not method.startswith('__') and
                not method.startswith('_')
            )

        for method_name in ex:
            method = getattr(cls.Create, method_name)
            method(uid)

    @classmethod
    def update(cls, member:'DiscordMember'):
        ex = tuple(
                method
                for method in dir(cls.Update)
                if callable(getattr(cls.Update, method)) and
                not method.startswith('__') and
                not method.startswith('_')
            )

        for method_name in ex:
            method = getattr(cls.Update, method_name)
            method(member)

    class Get():
        """獲取例外的資料庫資訊"""
        @staticmethod
        def star(uid:str) -> tuple[int,int]:
            """獲取星級,碎星值資訊

            Args:
                uid (str): 資料庫識別碼

            Returns:
                tuple[int,int]: 星級, 碎星值
            """
            db = SQL(db_account).connect(db_server).table(STARTABLE)
            data = db.select().where(db.id == uid).result.data
            del db

            if data.empty:
                return None
            return data.get("starLevel",1).values[0], data.get("brokenStar",0).values[0]


        @staticmethod
        def online_time(uid:str) -> tuple[str, int, bool]:
            """獲取上線時間資訊

            Args:
                uid (str): 資料庫識別碼

            Returns:
                tuple[str, int, bool]: 上線紀錄時間, 總上線時間, 當前是否在線
            """
            db = SQL(db_account).connect(db_server).table(ONLINETABLE)
            data = db.select(
                    SQLConvert.datetime.datestring('onlineTime'),
                    "total_onlineTime",
                    "isOnline"
                ).where(db.id == uid).result.data
            del db

            if data.empty:
                return None
            return data.get("onlineTime", '2019-12-25').values[0],\
                data.get("total_onlineTime", 0).values[0],\
                    data.get("isOnline", False).values[0]

    class Create():
        """資料庫創建擴增資訊"""
        @staticmethod
        def star(uid:str) -> None:
            """創建星級,碎星值資訊

            Args:
                uid (str): 資料庫識別碼
            """
            db = SQL(db_account).connect(db_server).table(STARTABLE)
            db.commit = True
            db.insert(
                    db.id, db.starLevel, db.brokenStar
                ).values(
                        uid, 1, 0
                    )
            del db

        @staticmethod
        def online_time(uid:str) -> None:
            """創建上線時間資訊

            Args:
                uid (str): 資料庫識別碼
            """
            db = SQL(db_account).connect(db_server).table(ONLINETABLE)
            db.commit = True
            db.insert(
                    db.id, db.onlineTime, db.total_onlineTime, db.isOnline
                ).values(
                        uid, '2019-12-25', 0, False
                    )
            del db

    class Update():
        """更新例外的資料庫資訊"""
        @staticmethod
        def star(member:'DiscordMember') -> None:
            """更新星級,碎星值資訊

            Args:
                uid (str): 資料庫識別碼
                star_level (int): 星級
                broken_star (int): 碎星值
            """
            db = SQL(db_account).connect(db_server).table(STARTABLE)
            db.commit = True
            db.update(
                    starLevel = member.star_level,
                    brokenStar = member.broken_star
                ).where(db.id == member.id)

            del db

        @staticmethod
        def online_time(member:'DiscordMember') -> None:
            """更新上線時間資訊

            Args:
                uid (str): 資料庫識別碼
                online_time (str): 上線紀錄時間
                total_online_time (int): 總上線時間
                is_online (bool): 當前是否在線
            """
            db = SQL(db_account).connect(db_server).table(ONLINETABLE)
            db.commit = True
            db.update(
                    onlineTime = member.online_time,
                    total_onlineTime = member.total_online_time,
                    isOnline = member.is_online
                ).where(
                        db.id == member.id
                    )
            del db

class DiscordMember(IDisocrdEntityInfo):
    """成員資訊"""
    def __init__(self, interaction:discord.Interaction) -> None:
        self._id:str
        self._name:str
        self._star_level:int
        self._broken_star:int
        self._online_time:str
        self._total_online_time:int
        self._is_online:bool
        self._sync:bool
        self._interaction = interaction
        self.user = DiscordUser(interaction)
        self.guild = DiscordGuild(interaction)
        self._db_get()

    def _db_get(self) -> None:
        self._name = self._interaction.user.display_name

        db = SQL(db_account).connect(db_server).table(INFOTABLE)

        data = db.select().where(
                (db.userId == self._interaction.user.id) &
                (db.guildId == self._interaction.guild.id)
            ).result.data
        del db

        if data.empty:
            self._db_create()
            self._db_get()

        else:
            self._id = data["id"].values[0]

            data = ExMember.get(self._id)

            if data["star"] is None or data["online_time"] is None:
                ExMember.create(self._id)
                self._star_level = 1
                self._broken_star = 0
                self._online_time = '2019-12-25'
                self._total_online_time = 0
                self._is_online = False
            else:
                self._star_level = data["star"][0]
                self._broken_star = data["star"][1]
                self._online_time = data["online_time"][0]
                self._total_online_time = data["online_time"][1]
                self._is_online = data["online_time"][2]

    def _db_create(self) -> None:
        db = SQL(db_account).connect(db_server).table(INFOTABLE)
        db.commit = True
        db.insert(
                db.userId,
                db.guildId
            ).values(
                    self._interaction.user.id,
                    self._interaction.guild.id
                )
        del db

        logger.write.info(
                F"已建立 {self._interaction.user.name}<{self._interaction.user.id}> "
                F"於 {self._interaction.guild.name}<{self._interaction.guild.id}> "
                "的伺服器資料",
                output=True
            )

    def db_update(self) -> None:
        if self._sync is False:
            return

        ExMember.update(self)

        self._sync = False

        logger.write.info(
                F"已更新 {self._interaction.user.name}<{self._interaction.user.id}> "
                F"於 {self._interaction.guild.name}<{self._interaction.guild.id}> "
                "的伺服器資料",
                output=True
            )

    @property
    def id(self) -> str:
        return self._id

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, new_name:str) -> None:
        self._name = new_name
        self._sync = True

    @property
    def star_level(self) -> int:
        """實體資訊星級"""
        return self._star_level

    @star_level.setter
    def star_level(self, new_star_level:int) -> None:
        self._star_level = new_star_level
        self._sync = True

    @property
    def broken_star(self) -> int:
        """實體資訊碎星值"""
        return self._broken_star

    @broken_star.setter
    def broken_star(self, new_broken_star:int) -> None:
        self._broken_star = new_broken_star
        self._sync = True

    @property
    def online_time(self) -> str:
        """實體資訊上線紀錄時間"""
        return self._online_time

    @online_time.setter
    def online_time(self, new_online_time:str) -> None:
        self._online_time = new_online_time
        self._sync = True

    @property
    def total_online_time(self) -> int:
        """實體資訊在線總時間"""
        return self._total_online_time

    @total_online_time.setter
    def total_onine_time(self, new_total_online_time:int) -> None:
        self._total_online_time = new_total_online_time
        self._sync = True

    @property
    def is_online(self) -> bool:
        """實體資訊是否在線"""
        return self._is_online

    @is_online.setter
    def is_online(self, new_is_online:bool) -> None:
        self._is_online = new_is_online
        self._sync = True

    @property
    def sync(self) -> bool:
        return self._sync
