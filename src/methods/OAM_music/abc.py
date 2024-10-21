#pylint:disable = C0114
from abc import ABC,abstractmethod

import discord

from .music import Music

class IMusicPlayer(ABC):
    """<Interface>提供音樂撥放器必要方法"""

    @abstractmethod
    def append(self, music:Music) -> None:
        pass

    @abstractmethod
    def pop(self, index:int = 0) -> Music:
        pass

    @abstractmethod
    async def start(self):
        """根據列表撥放音樂"""

    @abstractmethod
    async def shutdown(self) -> None:
        """清空撥放清單並且強制停止"""

    @abstractmethod
    async def skip(self) -> None:
        """跳過當前撥放的音樂"""

    @abstractmethod
    async def pause(self) -> None:
        """暫停音樂"""

    @abstractmethod
    async def resume(self) -> None:
        """恢復被暫停的音樂"""

    @abstractmethod
    def append_list(self, music_list, interaction) -> None:
        """新增撥放清單"""

    @property
    @abstractmethod
    def discord_voice_channel(self) -> discord.VoiceClient:
        """discord語音頻道位置"""

    @property
    @abstractmethod
    def music(self) -> Music:
        """當前播放的音樂"""

    @property
    @abstractmethod
    def msg(self) -> discord.Message:
        """discord訊息位置"""
