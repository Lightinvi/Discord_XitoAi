#pylint:disable = C0114
from random import choice

import os
import discord

from .abc import IMusicPlayer

STORAGE = "storage\\system\\music"

class MusicCheck():
    """處裡音樂撥放相關檢查"""
    @staticmethod
    def is_playerlist(url:str) -> bool:
        """檢查網址是否是youtube播放清單

        Args:
            url (str): youtube網址

        Returns:
            bool
        """
        if "playlist?list" in url:
            return True
        return False

    @staticmethod
    def is_url(string:str) -> bool:
        """檢查字串是否為youtube網址

        Args:
            string (str): 用戶輸入字串

        Returns:
            bool
        """
        if "music.youtube.com" in string or "youtube.com" in string or "youtu.be" in string:
            return True
        return False

    @staticmethod
    async def is_random(music:str) -> bool:
        """判斷是否為特殊指令 random"""
        if music != "!random":
            return music

        music = choice(os.listdir(STORAGE))
        music = music[:-4]
        return F"https://www.youtube.com/watch?v={music}"

    @staticmethod
    async def try_connect(
        interaction:discord.Interaction,
        music_player:IMusicPlayer
        ) -> discord.Message|None:
        """_summary_

        Args:
            interaction (Interaction): _description_
            music_console (MusicConsole): _description_

        Returns:
            discord.Message|None: _description_
        """
        if interaction.user.voice is None:
            return await interaction.followup.send("請加入任意語音頻道")

        try:
            music_player.discord_voice_channel = await interaction.user.voice.channel.connect()

        except discord.errors.ClientException:
            return await interaction.followup.send("頻道已被占用")
        return None
