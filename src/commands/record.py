import datetime
import discord

from discord import app_commands as Slash
from discord import Interaction
import discord.sinks

from src.core import CogExtension, Bot

FFMPEG = "C:\\ffmpeg\\bin\\ffmpeg.exe"
STORAGE = "storage\\system\\voice"

class Record(CogExtension):
    """語音頻道錄音"""
    def __init__(self, XitoAi) -> None:
        super().__init__(XitoAi)

        self.voice_client:discord.VoiceClient = None

    @Slash.command(name="start_record",description="test")
    async def start_record(self, interaction:Interaction):
        """開始錄音"""
        await interaction.response.defer()

        if interaction.user.voice is None:
            return await interaction.followup.send("請加入任意語音頻道")

        try:
            self.voice_client = await interaction.user.voice.channel.connect()

        except discord.errors.ClientException:
            return await interaction.followup.send("頻道已被占用")

        self.voice_client.start_recording(
            discord.sinks.MP4Sink(),
            self.cb,
            interaction.channel
        )

        await interaction.followup.send("Started recording")

    @Slash.command(name="stop_record", description="test")
    async def stop_record(self, interaction:Interaction):
        """結束錄音"""
        await interaction.response.defer()

        if self.voice_client is None:
            return await interaction.followup.send("沒有錄音事件可停止")
        try:
            self.voice_client.stop_recording()
        except discord.sinks.errors.RecordingException:
            await interaction.followup.send("錄製失敗")
        finally:
            await self.voice_client.disconnect()

        await interaction.followup.send("Stop recording")

    async def cb(self, sink:discord.sinks.Sink, channel:discord.TextChannel):
        """錄音結束後回呼"""
        strtime = datetime.datetime.now().strftime("%d%m%Y%H%M%S")
        recorded_users = [
        f"<@{user_id}>"
        for user_id, _ in sink.audio_data.items()
        ]

        await sink.vc.disconnect()
        files = []
        # files = [
        #         discord.File(audio.file, f"{user_id}{strtime}.{sink.encoding}")
        #         for user_id, audio in sink.audio_data.items()
        #     ]
        for user_id, audio in sink.audio_data.items():

            files.append(
                    discord.File(audio.file, f"{user_id}{strtime}.{sink.encoding}")
                )

            with open(F"{STORAGE}\\{user_id}{strtime}.{sink.encoding}", "wb") as f:
                f.write(audio.file.getbuffer())


        await channel.send(
                f"finished recording audio for: {', '.join(recorded_users)}", files=files
            )

async def setup(XitoAi:Bot):# pylint: disable=invalid-name
    # pylint: disable=missing-docstring
    await XitoAi.add_cog(Record(XitoAi))
