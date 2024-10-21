# pylint: disable= C0114,E1101
import discord

from src.core import SQL,db_account,db_server,Logger

from .interface import IDisocrdEntityInfo

TABLENAME:str = "userInfo"
logger = Logger()

class DiscordUser(IDisocrdEntityInfo):
    """使用者資訊
    """
    def __init__(self, interaction:discord.Interaction) -> None:
        self._id:str
        self._name:str
        self._email:str
        self._sync:bool = False
        self._interaction = interaction
        self._interaction = interaction
        self._db_get()

    def _db_get(self) -> None:
        self._id = str(self._interaction.user.id)

        db = SQL(db_account).connect(db_server).table(TABLENAME)
        data = db.select().where(db.userId == self._id).result.data
        del db

        if data.empty:
            self._name = self._interaction.user.name
            self._email = None
            self._db_create()
        else:
            self._name = data["userName"].values[0]
            self._email = data["email_address"].values[0]

    def _db_create(self) -> None:
        db = SQL(db_account).connect(db_server).table(TABLENAME)
        db.commit = True
        db.insert(
                db.userId, db.userName, db.email_address
            ).values(
                    self._id, self._name, self._email
                )

        del db
        logger.write.info(
                F"已建立用戶 -> {self._interaction.user.name}<{self._interaction.user.id}>",
                output=True
            )

    def db_update(self) -> None:
        if self._sync is False:
            return
        db = SQL(db_account).connect(db_server).table(TABLENAME)
        db.commit = True
        db.update(
                userId = self._id,
                userName = self._name,
                email_address = self._email
            ).where(
                    db.userId == self._id
                )

        self._sync = False

        del db

        logger.write.info(
                F"已更新用戶 -> {self._interaction.user.name}<{self._interaction.user.id}>",
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
    def email(self) -> str:
        """實體資訊電子郵件"""
        return self._email

    @email.setter
    def email(self, new_email) -> None:
        self._email = new_email
        self._sync = True

    @property
    def sync(self) -> bool:
        return self._sync
