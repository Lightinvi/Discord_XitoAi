# pylint: disable=invalid-name,E1101
"""夕由愛XitoAi主程式"""
import os
import asyncio
import discord
from discord.ext import commands
from src.core.logger import Logger
from src.core import SQL,db_account,db_server
from lang.translator import CommandTranslator

intents = discord.Intents.all()
intents.members = True
XitoAi = commands.Bot(command_prefix='admin!', intents=intents, case_insensitive=True)# pylint: disable=invalid-name
logger = Logger("logs\\setting.json")

@XitoAi.event
async def setup_hook():
    """初始化"""

    await XitoAi.tree.set_translator(CommandTranslator())

    sync = await XitoAi.tree.sync()

    for command_object in sync:
        logger.write.info(
                F"同步指令 -> {command_object.name}<{command_object.id}>",
                output=True
            )
    logger.write.info(F"已同步{len(sync)}個斜線指令",output=True)

    sql = SQL(db_account).connect(db_server)
    sql = sql.table('memberOnline')
    await sql.update(isOnline = 0).async_where(sql.isOnline == 1)

    del sql

@XitoAi.event
async def on_ready():
    """成功連入Discord服務時觸發
    """
    logger.write.info(" >>夕由愛XitoAi已成功連線Discord<< ",output=True)

@XitoAi.command('load')
@commands.check(428845649279188992)
async def load_command(ctx:commands.Context, extension:str):
    """載入擴充指令

    Args:
        ctx (commands.Context): 由discord.commands提供
        extension (str): 擴充指令檔案名稱
    """

    await XitoAi.load_extension(F'src.commands.{extension}')

    await ctx.channel.purge(limit=1)
    logger.write.info(F"擴充指令:{extension} 載入完成",output=True)

@XitoAi.command('unload')
@commands.check(428845649279188992)
async def unload_command(ctx:commands.Context, extension:str):
    """卸載擴充指令

    Args:
        ctx (commands.Context): 由discord.commands提供
        extension (str): 擴充指令檔案名稱
    """

    await XitoAi.unload_extension(F'src.commands.{extension}')

    await ctx.channel.purge(limit=1)
    logger.write.info(F"擴充指令:{extension} 卸載完成",output=True)

@XitoAi.command('reload')
@commands.check(428845649279188992)
async def reload_command(ctx:commands.Context, extension:str):
    """重載擴充指令

    Args:
        ctx (commands.Context): 由discord.commands提供
        extension (str): 擴充指令檔案名稱
    """

    await XitoAi.reload_extension(F'src.commands.{extension}')

    await ctx.channel.purge(limit=1)
    logger.write.info(F"擴充指令:{extension} 重載完成",output=True)

async def init_extension():
    """初始化擴充指令
    """

    for filename in os.listdir('./src./commands'):
        if filename.endswith('.py'):
            await XitoAi.load_extension(F'src.commands.{filename[:-3]}')

    logger.write.info("擴充指令初始化完成",output=True)

if __name__ == '__main__':
    VERSION = "release" #test | release

    sql_cmd = SQL(db_account).connect(db_server)
    sql_cmd = sql_cmd.table('token')
    result = sql_cmd.select().result.data
    token = result[result['version'] == VERSION]['token'].values[0]

    asyncio.run(init_extension())
    XitoAi.run(token)
