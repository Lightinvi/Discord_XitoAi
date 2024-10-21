import asyncio
import discord

from .ui import MusicUI
from .abc import IMusicPlayer
from .music import Music

FFMPEG = "C:\\ffmpeg\\bin\\ffmpeg.exe"
STORAGE = "storage\\system\\music"
class MusicPlayer(list, IMusicPlayer):
    """待撥放音樂控制器"""
    def __init__(self, XioAi):
        self.XitoAi = XioAi #pylint:disable = C0103
        self._discord_voice_channel:discord.VoiceClient = None
        self._music:Music|None = None
        self._msg:discord.Message = None

    def append(self, music:Music) -> None:

        if music.length < 600:
            return super(MusicPlayer, self).append(music) #pylint:disable = R1725
        raise TimeoutError

    def pop(self, index:int = 0) -> Music:
        return super(MusicPlayer, self).pop(index) #pylint:disable = R1725

    async def start(self):
        """根據列表撥放音樂"""

        if not self:
            if self._msg is None or self._music is None:
                return
            await self.shutdown()
            return
        self._music = self.pop()
        embed, view = MusicUI(self).show()
        if self._msg is None:
            self._msg = await self._music.discord_interaction.channel.send(embed=embed,view=view)
            msg:discord.WebhookMessage =\
                await self._music.discord_interaction.followup.send("音樂UI建置成功")
            await msg.delete(delay=10)
        else:
            await self._msg.edit(embed=embed,view=view)

        try:
            await self._music.download()
        except FileNotFoundError:
            return await self.start()

        self._discord_voice_channel.play(
            discord.FFmpegPCMAudio(
                executable=FFMPEG,
                source=F"{STORAGE}\\{self._music.id}.mp4"
                ),
            after=lambda _: asyncio.run_coroutine_threadsafe(self.start(),self.XitoAi.loop)
            )

    async def shutdown(self) -> None:
        """清空撥放清單並且強制停止"""
        try:
            self.clear()
            await self._discord_voice_channel.disconnect()
            await self._msg.delete()
        except AttributeError:
            pass
        except discord.errors.NotFound:
            pass
        finally:
            self._msg = None
            self._music = None
            self._discord_voice_channel = None

    async def skip(self):
        """跳過當前撥放的音樂"""
        self._discord_voice_channel.stop()

    async def pause(self) -> None:
        """暫停音樂"""
        self._discord_voice_channel.pause()

    async def resume(self) -> None:
        """恢復被暫停的音樂"""
        self._discord_voice_channel.resume()

    def append_list(self, music_list, interaction:discord.Interaction):
        """加入撥放清單"""
        music_list = list(music_list)
        if not music_list:
            return
        for url in music_list:

            try:
                self.append(Music(url, interaction))
            except TimeoutError:
                pass
            except OverflowError:
                pass

    @property
    def discord_voice_channel(self) -> discord.VoiceClient:
        return self._discord_voice_channel

    @discord_voice_channel.setter
    def discord_voice_channel(self, arg) -> None:
        self._discord_voice_channel = arg

    @property
    def music(self) -> Music:
        return self._music

    @music.setter
    def music(self, arg) -> None:
        self._music = arg

    @property
    def msg(self) -> discord.Message:
        return self._msg

    @msg.setter
    def msg(self, arg) -> None:
        self._msg = arg
