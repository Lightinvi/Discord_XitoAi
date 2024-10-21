from pytube import Playlist
from youtube_search import YoutubeSearch as YTSearch
import discord
import threading
from discord import app_commands as Slash
from src.core import CogExtension, Bot
from src.methods import MusicPlayer,MusicQueue,MusicCheck
from src.methods import Music as Music_

class Music(CogExtension):
    """音樂相關指令"""
    def __init__(self, XitoAi) -> None:
        super().__init__(XitoAi)
        self.music_console:MusicPlayer = MusicPlayer(self.XitoAi)

    @Slash.command(name="music",description="music.desc")
    @Slash.describe(music = "music.music.desc")
    async def play_music(self, interaction:discord.Interaction, music:str) -> None:
        """將音樂放置清單中並撥放

        Args:
            interactions (discord.Interaction): discord交互物件
            music (str): _description_ :音樂名稱或音樂網址(僅限youtube)

        """
        await interaction.response.defer()
        music = await MusicCheck.is_random(music)

        is_player_list:bool = False
        player_list:Playlist = None
        if await MusicCheck.try_connect(interaction,self.music_console):
            return

        is_player_list = MusicCheck.is_playerlist(music)
        if MusicCheck.is_url(music) and is_player_list:

            player_list = Playlist(music)
            if len(player_list.videos) < 1:
                await interaction.followup.send("無法加入播放清單: 播放清單無任何影片")
                return

            music_list = (x for x in player_list.video_urls)

            music_ = Music_(next(music_list), interaction)
            self.music_console.append(music_)

            t = threading.Thread(
                    target=self.music_console.append_list,
                    args=[music_list,interaction]
                )
            t.start()

        else:
            if MusicCheck.is_url(music):
                music_ = Music_(music, interaction)
            else:
                music = YTSearch(music, max_results=1).to_dict()
                music = F"https://www.youtube.com{music[0]['url_suffix']}"
                music_ = Music_(music, interaction)
            try:
                self.music_console.append(music_)
            except TimeoutError:
                await interaction.followup.send(F"無法加入播放清單: <{music_.title}> 超過10分鐘")
            except OverflowError:
                await interaction.followup.send("無法加入播放清單: 超出清單上限")

            if ((self.music_console.discord_voice_channel.is_playing()) or
                (self.music_console.music is not None)) and is_player_list is False:
                await interaction.followup.send(F"已將 <{music_.title}> 加入播放清單")
                return

        await self.music_console.start()

    @Slash.command(name="queue", description="queue.desc")
    async def music_queue(self, interaction:discord.Interaction):
        """查看待播列表"""
        msg:discord.Message = None

        await interaction.response.defer()
        if self.music_console:
            music_queue = MusicQueue(interaction,self.music_console)
            await music_queue.show()
        else:
            msg = await interaction.followup.send("音樂隊列中沒其他音樂")
            await msg.delete(delay=10)

    @Slash.command(name = "skip", description="skip.desc")
    async def skip_music(self, interaction:discord.Interaction):
        """跳過當前正在撥放的音樂

        Args:
            interaction (discord.Interaction): discord交互物件
        """
        await interaction.response.defer()
        if self.music_console.music is None:
            await interaction.response.send_message("沒有音樂可跳過")

        await interaction.followup.send("已跳過當前音樂")
        await self.music_console.skip()

    @Slash.command(name="pause", description="pause.desc")
    async def pause_music(self, interaction:discord.Interaction):
        """暫停當前撥放的音樂

        Args:
            interaction (discord.Interaction): discord交互物件
        """
        await interaction.response.defer()
        if ((self.music_console.music is None) and
            (self.music_console.discord_voice_channel.is_paused())):
            await interaction.followup.send("沒有音樂可暫停")

        await interaction.followup.send("已暫停當前音樂")
        await self.music_console.pause()

    @Slash.command(name="resume", description="resume.desc")
    async def resume_music(self, interaction:discord.Interaction):
        """恢復已暫停的音樂

        Args:
            interaction (discord.Interaction): discord交互物件
        """
        await interaction.response.defer()
        if ((self.music_console.music is None) and
            (self.music_console.discord_voice_channel.is_paused() is False)):
            await interaction.followup.send("沒有可恢復撥放的音樂")

        await interaction.followup.send("已恢復音樂撥放")
        await self.music_console.resume()

    @Slash.command(name="disconnect",description="disconnect.desc")
    async def dsiconnect_channel(self, interaction:discord.Interaction):
        """退出語音頻道並重置音樂清單

        Args:
            interaction (discord.Interaction): discord交互物件
        """
        await interaction.response.defer()

        if self.music_console.music is None or self.music_console.discord_voice_channel is None:
            await interaction.followup.send("播放器UI不存在")
        else:
            await interaction.followup.send("已退語音出頻道並關閉播放器UI")

        await self.music_console.shutdown()


async def setup(XitoAi:Bot):# pylint: disable=invalid-name
    # pylint: disable=missing-docstring
    await XitoAi.add_cog(Music(XitoAi))
