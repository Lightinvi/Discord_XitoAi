# pylint: disable=missing-docstring
from discord import RawReactionActionEvent,VoiceState,Message,Member,Guild,User
from src.methods import ReactionMethod,VoiceMethod,MessageMethod
from src.methods import DiscordGuild,FakeGuildInteraction,DiscordUser,FakeUserInteraction,DiscordMember
from src.core import CogExtension,Bot,Logger
logger = Logger()

class GuildEvent(CogExtension):
#https://discordpy.readthedocs.io/en/stable/api.html?highlight=join#discord.Guild

    @CogExtension.listener()
    async def on_guild_join(self, guild:Guild):
        #當被邀請進入公會 要求伺服器主設定相關事項(註:需思考身分驗證)
        #身分驗證邏輯參考https://discordpy.readthedocs.io/en/stable/api.html?highlight=join#discord.Role
        guild_owner:Member = guild.owner
        with open("systemDocumentation\\joinNewGuild.txt",'r',encoding='utf-8') as content:
            text = content.read()

        await guild_owner.send(text)

        guild = DiscordGuild(FakeGuildInteraction(guild))

        del guild

    @CogExtension.listener()
    async def on_guild_remove(self, guild:Guild):
        #當公會被移除 需刪除與公會相關的資料
        #觸發條件:
        # The client got banned.
        # The client got kicked.
        # The client left the guild.
        # The client or the guild owner deleted the guild.
        pass

    @CogExtension.listener()
    async def on_guild_update(self, before:Guild, after:Guild):
        #當公會更新資訊時更新資料庫 例如 公會名稱變更
        #處發條件:
        #任何公會屬性變更
        guild = DiscordGuild(FakeGuildInteraction(before))

        guild.name = after.name
        guild.system_channel = after.system_channel.id

        guild.db_update()

        del guild

class MemberEvent(CogExtension):

    @CogExtension.listener()
    async def on_member_join(self, member:Member):
        member = DiscordMember(FakeUserInteraction(member, member.guild))
        del member

    @CogExtension.listener()
    async def on_member_remove(self, member:Member):
        pass

    @CogExtension.listener()
    async def on_member_update(self, before:Member, after:Member):
        if self.XitoAi.user.id == before.id:
            return

        member = DiscordMember(FakeUserInteraction(before, before.guild))

        member.name = after.display_name

        member.db_update()

        del member

class UserEvent(CogExtension):

    @CogExtension.listener()
    async def on_user_update(self ,before:User, after:User):
        if self.XitoAi.user.id == before.id:
            return

        user = DiscordUser(FakeUserInteraction(before))

        user.name = after.name

        user.db_update()

        del user

class VoiceEvent(CogExtension):

    @CogExtension.listener()
    async def on_voice_state_update(self, member:Member, before:VoiceState, after:VoiceState):
        if member.id == self.XitoAi.user.id:
            return

        if before.channel is not None:
            before_channel = self.XitoAi.get_channel(before.channel.id)
        if after.channel is not None:
            after_channel = self.XitoAi.get_channel(after.channel.id)

        if before.channel is None and after.channel is not None:
            #當前公會紀錄時間
            await VoiceMethod.join_guild(member, after_channel.guild)

        elif before.channel is not None and after.channel is None:
            #當前公會結算時間
            await VoiceMethod.leave_guild(member,before_channel.guild)

        elif before_channel.guild.id != after_channel.guild.id:
            #結算前公會時間
            await VoiceMethod.leave_guild(member,before_channel.guild)
            #記錄當前公會時間
            await VoiceMethod.join_guild(member, after_channel.guild)

class MessageEvent(CogExtension):

    @CogExtension.listener()
    async def on_message(self, msg:Message):

        if msg.content == "ID:355" and msg.channel.id == 1146358218696691764:
            logger.write.info(
                F"{msg.author}<{msg.author}>:請求列印->"
                F"{msg.attachments[0].id}_{msg.attachments[0].filename}",
                output=True
                )
            await MessageMethod.print_data(msg.attachments[0])
            return

        if msg.author.id == self.XitoAi.user.id or msg.is_system():
            return

        if msg.attachments:
            for attachment in msg.attachments:
                await attachment.save(F".\\storage\\system\\{attachment.id}_{attachment.filename}")
            if msg.guild is None:
                logger.write.info(
                    F"{msg.author.name}<{msg.author.id}>私訊夕由愛新增附件:"
                    F"{tuple(F"{attachment.id}_{attachment.filename}"
                             for attachment in msg.attachments)}",
                    output=True
                    )
            else:
                logger.write.info(
                    F"{msg.author.name}<{msg.author.id}>在[{msg.guild.name}->{msg.channel.name}]"
                    F"新增附件:{tuple(F"{attachment.id}_{attachment.filename}"
                                  for attachment in msg.attachments)}",
                    output=True
                    )

        if msg.content:
            if msg.guild is None:

                developer = self.XitoAi.get_user(428845649279188992)
                await developer.send(F"{msg.author.name}<{msg.author.id}>私訊夕由愛:{msg.content}")
                logger.write.info(
                    F"{msg.author.name}<{msg.author.id}>私訊夕由愛:"
                    F"{msg.content}",
                    output=True
                    )
            else:
                logger.write.info(
                    F"{msg.author.name}<{msg.author.id}>在[{msg.guild.name}->{msg.channel.name}]說:"
                    F"{msg.content}",
                    output=True
                    )

            #if msg.content.startswith(F"<@{self.XitoAi.user.id}>"):

                #temp_msg = await msg.channel.send("XitoAi思考中......")
                #gpt = XitoAiGPT()

                # 使用 run_in_executor 將 generate 方法移動到執行緒池中運行
                #loop = asyncio.get_running_loop()
                #with ThreadPoolExecutor() as pool:
                    #await temp_msg.edit(
                            #content = await loop.run_in_executor(pool, gpt.generate, msg.content)
                        #)

    @CogExtension.listener()
    async def on_message_delete(self, msg:Message):
        if msg.author.id == self.XitoAi.user.id:
            return
        logger.write.info(
            F"{msg.channel.guild.name}<{msg.channel.guild.id}>"
            F" -> {msg.channel.name}<{msg.channel.id}>"
            F" 中的訊息被刪除: {msg.content}",
            output=True
        )

    @CogExtension.listener()
    async def on_message_edit(self, before:Message, after:Message):
        if before.author.id == self.XitoAi.user.id:
            return
        logger.write.info(
            F"{before.channel.guild.name}<{before.channel.guild.id}>"
            F" -> {before.channel.name}<{before.channel.id}>"
            F" 中的訊息被編輯: {before.content} -> {after.content}",
            output=True
        )

class ReactionEvent(CogExtension):

    @CogExtension.listener()
    async def on_raw_reaction_add(self, payload:RawReactionActionEvent):

        emoji = payload.emoji

        translation_ch = self.XitoAi.get_channel(payload.channel_id)
        translation_msg = await translation_ch.fetch_message(payload.message_id)

        response = ReactionMethod.msg_translation(emoji, translation_msg.content)

        if response:
            await translation_ch.send(response)


async def setup(XitoAi:Bot):# pylint: disable=invalid-name
    await XitoAi.add_cog(GuildEvent(XitoAi))
    await XitoAi.add_cog(MemberEvent(XitoAi))
    await XitoAi.add_cog(UserEvent(XitoAi))
    await XitoAi.add_cog(VoiceEvent(XitoAi))
    await XitoAi.add_cog(MessageEvent(XitoAi))
    await XitoAi.add_cog(ReactionEvent(XitoAi))
