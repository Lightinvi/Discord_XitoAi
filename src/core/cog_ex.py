"""cog和sql帳號登陸引用"""

from discord import app_commands as Slash
from discord.ext import commands
from discord.ext.commands import Bot # pylint: disable=unused-import

from lang.translator import ContentTranslator

class CogExtension(commands.Cog):
    """擴充類別導入"""

    def __init__(self,XitoAi) -> None:# pylint: disable=invalid-name
        super().__init__()
        self.XitoAi:Bot = XitoAi# pylint: disable=invalid-name
        self.content = ContentTranslator().translate
