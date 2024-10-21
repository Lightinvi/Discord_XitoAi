import datetime
import discord

class ProfileCheck():

    @staticmethod
    def is_personal(interaction:discord.Interaction) -> bool:
        """檢查是否為私人訊息

        Args:
            interaction (discord.Interaction): 交互物件

        Returns:
            bool: 若為私人訊息回傳True
        """
        if interaction.guild is None:
            return True

        return False

    @staticmethod
    def is_verify(email_address:str|None) -> bool:
        """檢查郵件是否驗證

        Args:
            email_address (str): 郵件地址

        Returns:
            bool: 若以驗證回傳True
        """
        if email_address is None:
            return False
        if '@' in email_address and '*' not in email_address:
            return True

        return False

    @staticmethod
    def online_time(is_online:bool, start_time:str) -> str:
        if is_online:
            start_time = datetime.datetime.strptime(start_time[:-7],'%Y-%m-%d %H:%M:%S')
            return str(datetime.datetime.now() - start_time)

        return "0"
