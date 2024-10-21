
from math import ceil
import threading
from youtube_search import YoutubeSearch as YTSearch
from pytube import Playlist
import discord

from .abc import IMusicPlayer
from .check import MusicCheck
from .music import Music

class MusicQueue():
    """音樂待播清單介面 使用時確定使用defer延遲請讓此物件去送出訊息"""
    def __init__(self, interaction:discord.Interaction, music_queue:list[Music]) -> None:
        self.interaction = interaction
        self.msg:discord.Message = None
        self.now_page:int = 0
        self.total_page = ceil(float(len(music_queue)/5))
        self.pages:list[discord.Embed] = []
        self.generator = self.gnerate_page(music_queue)

    @property
    def view(self):
        """按鈕UI"""
        v = discord.ui.View()

        v.add_item(self.BackButton(self))
        v.add_item(self.NextButton(self))

        return v

    async def show(self) -> None:
        """顯示/更改清單"""
        if self.msg:
            await self.msg.edit(
                embed=self.pages[self.now_page],
                view=self.view
            )
        else:
            self.pages.append(next(self.generator))
            self.msg = await self.interaction.followup.send(
                    embed=self.pages[self.now_page],
                    view=self.view
                )
            await self.msg.delete(delay=600)

    def gnerate_page(self, music_queue:list[Music]):
        """創建單頁頁面"""

        page_number:int = 1
        page = discord.Embed(
            title="音樂待播清單",
            description=F"{page_number}/{self.total_page}"
            )
        for num,music in enumerate(music_queue):
            num += 1
            page.add_field(
                name=music.title,
                value=F"{int((music.length/60))}分{int((music.length%60))}秒",
                inline=False
                )
            if num%5 == 0:
                yield page
                page_number += 1
                page = discord.Embed(
                    title="音樂待播清單",
                    description=F"{page_number}/{self.total_page}"
                )
        yield page

    async def next(self) -> None:
        """更換下一頁"""
        if page := next(self.generator):
            self.pages.append(page)
        self.now_page += 1
        if self.now_page > self.total_page-1:
            self.now_page = 0

    async def back(self) -> None:
        """更換上一頁"""
        self.now_page -= 1
        if self.now_page < 0:
            self.now_page = self.total_page-1

    class NextButton(discord.ui.Button):
        """下一頁按鈕"""
        def __init__(self, music_queue:'MusicQueue'):
            super().__init__(emoji="➡")
            self.music_queue = music_queue
        async def callback(self, interaction: discord.Interaction):
            await interaction.response.send_message("Loading",delete_after=0.1)
            await self.music_queue.next()
            await self.music_queue.show()

    class BackButton(discord.ui.Button):
        """上一頁按鈕"""
        def __init__(self, music_queue:'MusicQueue'):
            super().__init__(emoji="⬅️")
            self.music_queue = music_queue
        async def callback(self, interaction: discord.Interaction):
            await interaction.response.send_message("Loading",delete_after=0.1)
            await self.music_queue.back()
            await self.music_queue.show()

class MusicUI():
    """音樂操作介面"""
    def __init__(self, player:IMusicPlayer) -> None:
        self.player = player

    @property
    def embed(self) -> discord.Embed:
        """音樂資訊

        Returns:
            discord.Embed: discord音樂訊息版
        """
        embed_ = discord.Embed(color=discord.Color.random())

        embed_.title = self.player.music.title
        embed_.url = self.player.music.url
        embed_.description = "Now playing"
        embed_.set_thumbnail(url=self.player.music.thunbnail_url)

        embed_.add_field(
            name="音樂時長",
            value=F"{int((self.player.music.length/60))}分{int((self.player.music.length%60))}秒",
            inline=True
            )
        embed_.add_field(
            name="音樂上傳者",
            value=self.player.music.author,
            inline=True
        )
        embed_.add_field(
            name="音樂播放者",
            value=self.player.music.player
        )

        return embed_

    @property
    def view(self) -> discord.ui.View:
        """音樂操作按鈕

        Returns:
            discord.ui.View: discord音樂操作view
        """
        v = discord.ui.View(timeout=None)

        v.add_item(self.QueueButton(self.player))
        v.add_item(self.AddMusicButton(self.player))
        v.add_item(self.PlayPauseButton(self.player))
        v.add_item(self.SkipButton(self.player))
        v.add_item(self.StopButton(self.player))

        return v

    def show(self) -> tuple[discord.Embed,discord.ui.View]:
        """完整Discord音樂資訊版

        Returns:
            tuple[discord.Embed,discord.ui.View]: 包含資訊與操作介面
        """
        return self.embed,self.view

    class SkipButton(discord.ui.Button):
        """跳過按鈕"""
        def __init__(self, player:IMusicPlayer):
            super().__init__(emoji="⏭")
            self.player = player

        async def callback(self, interaction: discord.Interaction):
            await interaction.response.defer()
            await self.player.skip()
            msg:discord.WebhookMessage = await interaction.followup.send("已跳過")
            await msg.delete(delay=10)

    class PlayPauseButton(discord.ui.Button):
        """開始/暫停按鈕"""
        def __init__(self, player:IMusicPlayer):
            super().__init__(emoji="⏯")
            self.player = player

        async def callback(self, interaction: discord.Interaction):
            await interaction.response.defer()
            if self.player.discord_voice_channel.is_paused():
                await self.player.resume()
                msg:discord.WebhookMessage = await interaction.followup.send("已恢復")
                await msg.delete(delay=10)
            else:
                await self.player.pause()
                msg:discord.WebhookMessage = await interaction.followup.send("已暫停")
                await msg.delete(delay=10)

    class QueueButton(discord.ui.Button):
        """音樂清單按鈕"""
        def __init__(self, player:IMusicPlayer):
            super().__init__(emoji="🎵")
            self.player = player

        async def callback(self, interaction: discord.Interaction):
            msg:discord.Message = None

            await interaction.response.defer()
            if self.player:
                music_queue = MusicQueue(interaction,self.player)
                await music_queue.show()

            else:
                msg = await interaction.followup.send("音樂隊列中沒其他音樂")
                await msg.delete(delay=10)

    class StopButton(discord.ui.Button):
        """暫停/退出按鈕"""
        def __init__(self, player:IMusicPlayer):
            super().__init__(emoji="⏹")
            self.player = player

        async def callback(self, interaction: discord.Interaction):
            await interaction.response.defer()
            await self.player.shutdown()
            msg:discord.Message = await interaction.followup.send("已關閉音樂UI介面")
            await msg.delete(delay=10)

    class AddMusicButton(discord.ui.Button):
        """添加音樂按鈕"""
        def __init__(self, player:IMusicPlayer):
            super().__init__(emoji="⏏")
            self.player = player

        async def callback(self, interaction):

            await interaction.response.send_modal(self.AddMusicTextinput(self.player))

        class AddMusicTextinput(discord.ui.Modal):
            """添加音樂輸入框"""
            def __init__(self, player:IMusicPlayer):
                super().__init__(title="添加音樂")
                self.player = player
                self.add_item(discord.ui.TextInput(label="歌曲名稱或網址",required=True))

            async def on_submit(self, interaction: discord.Interaction) -> None:#pylint:disable = w0221
                await interaction.response.defer()
                music = await MusicCheck.is_random(self.children[0].value)

                msg:discord.Message = None
                is_player_list = MusicCheck.is_playerlist(music)
                if MusicCheck.is_url(music) and is_player_list:
                    if (is_player_list := MusicCheck.is_playerlist(music)):

                        player_list = Playlist(music)
                        music_list = (x for x in player_list.video_urls)

                        music_ = Music(next(music_list), interaction)
                        self.player.append(music_)

                        t = threading.Thread(
                                target=self.player.append_list,
                                args=[music_list, interaction]
                            )
                        t.start()
                        return
                else:
                    if MusicCheck.is_url(music):
                        music_ = Music(music, interaction)
                    else:
                        music = YTSearch(music, max_results=1).to_dict()
                        music = F"https://www.youtube.com{music[0]['url_suffix']}"
                        music_ = Music(music, interaction)
                    try:
                        self.player.append(music_)
                        msg = await interaction.followup.send(F"已將 <{music_.title}> 加入播放清單")
                    except TimeoutError:
                        msg = await interaction.followup.send(F"無法加入播放清單: <{music_.title}> 超過10分鐘")
                    except OverflowError:
                        msg = await interaction.followup.send("無法加入播放清單: 超出清單上限")
                    finally:
                        await msg.delete(delay=10)
