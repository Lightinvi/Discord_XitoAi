#pylint:disable = C0114 
import os
import discord
import yt_dlp

from src.core.logger import Logger
logger = Logger()

STORAGE = "storage\\system\\music"

class Music():
    """音樂物件, 當搜尋到youtube資料後將其儲存至此物件
    """
    def __init__(self, url:str, discord_interaction:discord.Interaction) -> None:
        self.url:str = url
        self.discord_interaction:discord.Interaction = discord_interaction
        ydl_opts = {}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            self._youtube_info = ydl.extract_info(self.url, download=False)

    @property
    def youtube_info(self) -> dict:
        """使用 yt-dlp 獲取影片資訊"""
        return self._youtube_info

    @property
    def id(self) -> str:
        """此音樂在youtube的識別碼"""
        return self.youtube_info.get('id', '')

    @property
    def title(self) -> str:
        """此音樂在youtube上的標題"""
        return self.youtube_info.get('title', 'Unknown Title')

    @property
    def author(self) -> str:
        """此音樂在youtube上的上傳者"""
        return self.youtube_info.get('uploader', 'Unknown Author')

    @property
    def length(self) -> int:
        """此音樂在youtube上的影片長度"""
        return self.youtube_info.get('duration', 0)

    @property
    def thunbnail_url(self) -> str:
        """此音樂在youtube上的影片縮圖"""
        return self.youtube_info.get('thumbnail', '')

    @property
    def player(self) -> str:
        """此音樂的撥放者"""
        return self.discord_interaction.user.name

    async def download(self) -> None:
        """下載音樂至儲存庫中(若音樂檔案已存在或略過下載)"""
        if os.path.isfile(F"{STORAGE}\\{self.id}.mp4"):
            return
        try:
            ydl_opts = {
                'format': 'bestaudio/best',
                'outtmpl': f"{STORAGE}\\{self.id}.mp4"
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([self.url])
        except Exception as ex:
            logger.write.warning(ex,output=True)
            raise FileNotFoundError#pylint:disable=W0707
