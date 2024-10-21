# pylint: disable=invalid-name, E1101
# pylint: disable=missing-docstring
import datetime
import win32print
import win32con
import win32ui
from PIL import Image,ImageWin
from discord import PartialEmoji
from discord import Attachment,Member,Guild
from googletrans import Translator
from src.methods import DiscordMember,FakeUserInteraction,ProfileCheck
from src.core import SQL,db_account,db_server,Logger
logger = Logger()

class MessageMethod():
    @staticmethod
    async def is_verify(user_id):
        sql_cmd = SQL(db_account).connect(db_server)
        sql_cmd = sql_cmd.table('userInfo')
        result = await sql_cmd.select('email_address').where(sql_cmd.userId == user_id).async_result
        del sql_cmd
        result = result.data
        if ('@' in result['email_address'].values[0] and
            '*' not in result['email_address'].values[0]):
            return True
        return False

    @staticmethod
    async def print_data(image:Attachment):
        await image.save(F".\\storge\\system\\{image.id}_{image.filename}")

        # image_ = Image.open(F".\\storge\\system\\{image.filename}")

        # if image_.size[0] > image_.size[1]:
        #     image_ = image_.rotate(90)

        # printername = win32print.GetDefaultPrinter()

        # hprinter = win32print.OpenPrinter(printername)

        # hdc = win32ui.CreateDC()
        # hdc.CreatePrinterDC(printername)
        # hdc.StartDoc(image.filename)
        # hdc.StartPage()

        # hdc.SetMapMode(win32con.MM_TWIPS)
        # hdc.DrawBitmap(image_.GetBitmapHandle(), (100, 100, 2000, 2000))

        # hdc.EndPage()
        # hdc.EndDoc()

        # win32print.ClosePrinter(hprinter)

class VoiceMethod():

    @staticmethod
    async def join_guild(member:Member,guild:Guild):
        member_profile = DiscordMember(FakeUserInteraction(member,guild))

        member_profile.online_time = datetime.datetime.now()
        member_profile.is_online = True

        member_profile.db_update()

        logger.write.info(
            F"{member.name}<{member.id}>"
            F" 加入 {guild.name}<{guild.id}> 的語音頻道",
            output=True
            )

    @staticmethod
    async def leave_guild(member:Member,guild:Guild):

        member_profile = DiscordMember(FakeUserInteraction(member,guild))

        if not member_profile.is_online:
            logger.write.warning(F"{member.name}<{member.id}> 異常上線時間紀錄", output=True)
            return

        diff_time:datetime = datetime.datetime.now() -\
            datetime.datetime.strptime(member_profile.online_time[:-7],'%Y-%m-%d %H:%M:%S')

        member_profile.total_onine_time += int(int(diff_time.total_seconds())/60)
        member_profile.is_online = False

        if ProfileCheck.is_verify(member_profile.user.email):
            broken_star = int(2*int(int(diff_time.total_seconds())/60))
        else:
            broken_star = int(1.5*int(int(diff_time.total_seconds())/60))

        member_profile.broken_star += broken_star

        member_profile.db_update()

        logger.write.info(
            F"{member.name}<{member.id}>"
            F" 於 {guild.name}<{guild.id}>"
            F" 獲得 {int(int(diff_time.total_seconds())/60)}貢獻值 和 {broken_star}碎星值",
            output=True
            )


class ReactionMethod():

    @staticmethod
    def msg_translation(emoji:PartialEmoji,msg:str) -> str | None:
        translator = Translator()
        emoji_dict = {
            '🇹🇼':'zh-tw',
            '🇯🇵':'ja',
            '🇨🇳':'zh-cn',
            '🇬🇧':'en',
            '🇺🇸':'en'
        }
        dest = emoji_dict.get(str(emoji), None)

        return translator.translate(
            text=msg,
            dest=dest
            ).text

    @staticmethod
    def none() -> None:
        return None
