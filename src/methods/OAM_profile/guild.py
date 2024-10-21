# pylint: disable= C0114,E1101
import discord

from src.core import SQL,db_account,db_server,Logger

from .interface import IDisocrdEntityInfo
logger = Logger()

TABLENAME:str = "guildInfo"

class DiscordGuild(IDisocrdEntityInfo):
    """公會資訊
    """

    def __init__(self, interaction:discord.Interaction) -> None:
        self._id:str
        self._name:str
        self._sync:bool
        self._system_channel:str
        self._interaction = interaction
        self._db_get()

    def _db_get(self) -> None:
        self._id = str(self._interaction.guild.id)

        db = SQL(db_account).connect(db_server).table(TABLENAME)
        data = db.select().where(db.guildId == self._id).result.data
        del db

        if data.empty:
            self._name = self._interaction.guild.name

            if self._interaction.guild.system_channel:
                self._system_channel = self._interaction.guild.system_channel.id
            else:
                self._system_channel = None

            self._db_create()
        else:
            self._name = data["guildName"].values[0]
            self._email = data["systemChannelId"].values[0]

    def _db_create(self) -> None:
        db = SQL(db_account).connect(db_server).table(TABLENAME)
        db.commit = True
        db.insert(
                db.guildId, db.guildName, db.systemChannelId
            ).values(
                    self._id, self._name, self._system_channel
                )

        del db

        logger.write.info(
                F"已建立公會 -> {self._interaction.guild.name}<{self._interaction.guild.id}>",
                output=True
            )

    def db_update(self) -> None:
        if self._sync is False:
            return
        db = SQL(db_account).connect(db_server).table(TABLENAME)
        db.commit = True
        db.update(
                guildId = self._id,
                guildName = self._name,
                systemChannelId = self._system_channel
            ).where(
                    db.guildId == self._id
                )

        self._sync = False

        del db

        logger.write.info(
                F"已更新公會 -> {self._interaction.guild.name}<{self._interaction.guild.id}>",
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
    def system_channel(self) -> str:
        """實體資訊系統頻道"""
        return self._system_channel

    @system_channel.setter
    def system_channel(self, new_system_channel_id) -> None:
        self._system_channel = new_system_channel_id
        self._sync = True

    @property
    def sync(self) -> bool:
        return self._sync
