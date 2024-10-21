#pylint:disable=C0114
import discord

from .interface import IFakeInteraction

class FakeUserInteraction(IFakeInteraction):
    """使discord.User物件偽裝成discord.interaction,方便於資料庫讀取
    """
    def __init__(
            self,
            user:discord.User|discord.Member,
            guild:discord.Guild = None
        ) -> None:
        """使discord.User物件偽裝成discord.interaction,方便於資料庫讀取

        Args:
            user (discord.User | discord.Member): 用戶或成員
            guild (guild, optional): 公會(不提供時無法guild資訊)
        """
        self._user = user

        if guild is None:
            self._guild = None
        else:
            self._guild = guild

    @property
    def user(self) -> discord.User|discord.Member:
        return self._user

    @property
    def guild(self) -> discord.Guild:
        return self._guild

class FakeGuildInteraction(IFakeInteraction):
    """使discord.Guild物件偽裝成discord.interaction,方便於資料庫讀取
    """
    def __init__(
            self,
            guild:discord.Guild,
            user:discord.User = None
        ) -> None:
        """使discord.Guild物件偽裝成discord.interaction,方便於資料庫讀取

        Args:
            guild (discord.Guild): 公會
            user (discord.Interaction, optional): 用戶或成員(不提供時無法user資訊)
        """
        if user is None:
            self._user = None
        else:
            self._user = user

        self._guild = guild

    @property
    def user(self) -> discord.User|discord.Member:
        return self._user

    @property
    def guild(self) -> discord.Guild:
        return self._guild
