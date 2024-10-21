# pylint: disable=missing-docstring
import discord
from discord import app_commands as Slash
from discord import Interaction,Embed
from src.core import Optional
from src.core import CogExtension, Bot
from src.methods import DiscordMember
from src.methods import LotteryMethod,ErrorMsgBox,LotteryBox


class Entertainment(CogExtension):

    @Slash.command(name="lottery", description="lottery.desc")
    @Slash.describe(broken_star="lottery.broken_star.desc")
    async def lottery(
        self,
        interaction:Interaction,
        broken_star:int = 1000
        ) -> Optional[LotteryBox|ErrorMsgBox]:

        locale = interaction.locale
        member = DiscordMember(interaction)

        if check := LotteryMethod.is_in_range(member,broken_star):
            lottery_result = check
        else:
            lottery_result = LotteryMethod.lottery_machine(broken_star)

            member.broken_star -= broken_star
            member.broken_star += lottery_result.bonus

            member.db_update()

        if isinstance(lottery_result,ErrorMsgBox):

            return await interaction.response.send_message(
                    self.content(F"lottery.error.msg.{lottery_result.msg}", locale)
                )

        embed = Embed(
            title=self.content("lottery.result",locale),
            description=F"{self.content("lottery.bet", locale)}: {broken_star}"
            )

        embed.add_field(
                name = self.content("lottery.magnification", locale),
                value = lottery_result.magnification
            )
        embed.add_field(
                name = self.content("lottery.probability", locale),
                value = F"{float(lottery_result.probability)*100}%"
            )
        embed.add_field(
                name = self.content("lottery.bouns", locale),
                value = lottery_result.bonus
            )

        return await interaction.response.send_message(embed=embed)

async def setup(XitoAi:Bot):# pylint: disable=invalid-name
    await XitoAi.add_cog(Entertainment(XitoAi))
