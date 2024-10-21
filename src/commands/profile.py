#pylint:disable =C0114,C0115
import discord

from src.core import CogExtension,Bot,Slash
from src.methods import DiscordMember,ProfileCheck,LevelMethod,FakeUserInteraction,MemberRank

class Profile(CogExtension):

    @Slash.command(name="me", description="me.desc")
    async def view_self_profile(self, interaction:discord.Interaction):
        """查看個人於當前公會的資訊"""
        lang = interaction.locale

        if ProfileCheck.is_personal(interaction):
            return await interaction.response.send_message(
                    self.content("me.is_personal",lang)
                )

        member = DiscordMember(interaction)

        online_time = ProfileCheck.online_time(member.is_online, member.online_time)

        if ProfileCheck.is_verify(member.user.email):
            verify_string = self.content("me.verify", lang)
        else:
            verify_string = self.content("me.unverify", lang)

        embed = discord.Embed(title = member.guild.name,color=discord.Color.random())

        embed.add_field(
            name = self.content("me.starLevel",lang),
            value = LevelMethod.convert(member.star_level),
            inline= False
        )
        embed.add_field(
            name = self.content("me.brokenStar",lang),
            value = member.broken_star,
            inline= True
        )
        embed.add_field(
            name = self.content("me.total_online_time",lang),
            value = member.total_online_time,
            inline= False
        )
        embed.add_field(
            name = self.content("me.current_online_time",lang),
            value = online_time,
            inline= True
        )
        embed.add_field(
            name = self.content("me.verify_status",lang),
            value = verify_string,
            inline= False
        )

        if interaction.user.display_avatar:
            avatar_url = interaction.user.display_avatar.url
        else:
            avatar_url = None

        embed.set_author(name=member.name, icon_url=avatar_url)

        await interaction.response.send_message(embed= embed)

    @Slash.command(name="other", description="other.desc")
    @Slash.describe(user="other.user.desc")
    async def view_other_profile(
            self,
            interaction:discord.Interaction,
            user:discord.User|discord.Member
        ):
        """於當前公會查看他人資訊"""
        lang = interaction.locale

        if ProfileCheck.is_personal(interaction):
            return await interaction.response.send_message(
                    self.content("other.is_personal",lang)
                )

        member = DiscordMember(FakeUserInteraction(user,interaction.guild))

        online_time = ProfileCheck.online_time(member.is_online, member.online_time)

        embed = discord.Embed(title = member.guild.name,color=discord.Color.random())

        embed.add_field(
            name = self.content("other.starLevel",lang),
            value = LevelMethod.convert(member.star_level),
            inline= False
        )
        embed.add_field(
            name = self.content("other.brokenStar",lang),
            value = member.broken_star,
            inline= True
        )
        embed.add_field(
            name = self.content("other.total_online_time",lang),
            value = member.total_online_time,
            inline= False
        )
        embed.add_field(
            name = self.content("other.current_online_time",lang),
            value = online_time,
            inline= True
        )

        if user.display_avatar:
            avatar_url = user.display_avatar.url
        else:
            avatar_url = None

        embed.set_author(name=member.name, icon_url=avatar_url)

        await interaction.response.send_message(embed= embed)

    @Slash.command(name="rank", description="rank.desc")
    @Slash.describe(target="rank.target.desc", index="rank.index.desc")
    @Slash.choices(
        target = [
            Slash.Choice(name = "rank.choice.brokenStar", value="brokenStar"),
            Slash.Choice(name="rank.choice.onlineTime", value="total_onlineTime")
        ]
    )
    async def rank(self, interaction:discord.Interaction, target:str, index:int = 3):
        if interaction.guild is None:
            await interaction.response.send_message(
                    "You can only use this command in a guild"
                )
        if index <= 0:
            await interaction.response.send_message(
                    self.content("rank.index.rangeout", interaction.locale)
                )
            return

        local_target = F"rank.{target}"
        output:str =\
            F"{interaction.guild.name}-{self.content(local_target, interaction.locale)}排行\n"
        rank_list = MemberRank(interaction.guild.id)
        result = rank_list.rank_target(target, index)
        for num,data in enumerate(result.values):
            output += F"#{num+1} -> <@{data[0]}> : {data[1]}\n"

        await interaction.response.send_message(output)

async def setup(XitoAi:Bot):# pylint: disable=invalid-name
    # pylint: disable=missing-docstring
    await XitoAi.add_cog(Profile(XitoAi))
