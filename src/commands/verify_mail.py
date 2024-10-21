# pylint: disable=missing-docstring
from discord import app_commands as Slash
from discord import Interaction

from src.core import CogExtension, Bot, Logger
from src.methods import DiscordUser,generate_verify_code,send_verify_mail
logger = Logger()

class VerifyMail(CogExtension):
    """電子郵件認證"""

    @Slash.command(name="get_verification", description="get_verification.desc")
    @Slash.describe(email = "get_verification.email.desc")
    async def verify_mail(self, interaction:Interaction, email:str) -> None:
        """寄送驗證信件

        Args:
            interaction (Interaction): 由Discord提供相關交互訊息
            email (str): 使用者信箱
        """
        await interaction.response.defer()
        locale = interaction.locale
        user = DiscordUser(interaction)

        if user.email is not None:
            if '@' in user.email and '*' not in user.email:
                return await interaction.followup.send(
                        self.content("verify.completed", locale)
                    )

        code = generate_verify_code()

        user.email = email + F'*{code}'
        user.db_update()

        await send_verify_mail(interaction.user.name, email, code)
        logger.write.info(F"寄送驗證碼至 {email}({interaction.user.name}):{code}",output=True)

        await interaction.followup.send(
                self.content("verify.sent", locale)
            )

    @Slash.command(name='verify', description='verify.desc')
    @Slash.describe(code="verify.code.desc")
    async def verify_code(self, interaction:Interaction, code:str) -> None:
        """驗證碼認證

        Args:
            interaction (Interaction): 由Discord提供相關交互訊息
            code (str): 驗證碼
        """
        await interaction.response.defer()
        locale = interaction.locale
        user = DiscordUser(interaction)

        if user.email is not None:
            if '@' in user.email and '*' not in user.email:
                return await interaction.followup.send(
                        self.content("verify.completed", locale)
                    )

            db_code = user.email.split('*')[1]

            if code == db_code:
                user.email = user.email.split('*')[0]
                user.db_update()
                logger.write.info(F"{interaction.user.name} 驗證成功")
                return await interaction.followup.send(
                        self.content("verify.succeed", locale)
                    )
            logger.write.info(F"{interaction.user.name} 驗證失敗")
            return await interaction.followup.send(
                        self.content("verify.failed", locale)
                    )
        logger.write.info(F"{interaction.user.name} 驗證失敗")
        return await interaction.followup.send(
                        self.content("verify.failed", locale)
                    )

async def setup(XitoAi:Bot):# pylint: disable=invalid-name
    # pylint: disable=missing-docstring
    await XitoAi.add_cog(VerifyMail(XitoAi))
