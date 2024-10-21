import os
import json
import discord
from discord.app_commands.translator import locale_str

class ContentTranslator():
    """內文翻譯"""
    def __init__(self) -> None:
        self.content_dictionary:dict = self.generate_dictionary()
        self.default:dict = self.content_dictionary["en-US"]

    def generate_dictionary(self) -> dict:
        """生成內文用翻譯字典"""
        result = {}
        for file in os.listdir(".\\lang"):
            if not file.endswith(".json"):
                continue

            with open(F"lang\\{file}", "r", encoding="utf-8") as lang_file:
                lang = json.load(lang_file)

            result[file[:-5]] = lang["content"]
        return result

    def translate(self, string:str, locale:discord.Locale = discord.Locale("en-US")):
        """將內文轉換成指定的語言(預設英文)"""
        # return self.content_dictionary.get(locale.value, {}).get(string, string)
        return self.content_dictionary.get(
                locale.value,
                {}
            ).get(
                    string,
                    self.default.get(string, "Display error")
                )

class CommandTranslator(discord.app_commands.Translator):
    """指令翻譯"""
    def __init__(self) -> None:
        super().__init__()
        self.command_dictionary:dict = self.generate_dictionary()
        self.default:dict = self.command_dictionary["en-US"]

    def generate_dictionary(self) -> dict:
        """生成指令用翻譯字典"""
        result = {}
        for file in os.listdir(".\\lang"):
            if not file.endswith(".json"):
                continue

            with open(F"lang\\{file}", "r", encoding="utf-8") as lang_file:
                lang = json.load(lang_file)

            result[file[:-5]] = lang["command"]
        return result

    async def translate(self, string: locale_str, locale: discord.Locale, context) -> str | None:

        return self.command_dictionary.get(locale.value, {}).get(string.message, string.message)
        # return self.command_dictionary.get(
        #         locale.value,
        #         {}
        #     ).get(
        #             string.message,
        #             self.default.get(string.message, "Display error")
        #         )
