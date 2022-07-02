import os
import discord
from discord import app_commands
from discord.ext import commands
from datetime import timedelta

ModPermissionID = int(os.getenv("ModPermissionID"))
testServerID = discord.Object(id=int(os.getenv("testServerIDInt")))


class Mod(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    # @commands.bot_has_permissions(manage_messages=True)
    @app_commands.checks.has_any_role("WeiTing", "Mod", ModPermissionID)
    @app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.guild_id, i.user.id))
    @app_commands.command(name="clear", description="清除訊息，需指定數量")
    async def clearMessages(self, interaction: discord.Interaction, amount: int) -> None:
        deleted = await interaction.channel.purge(limit=amount)
        await interaction.response.send_message(f"已清除 {len(deleted)} 則訊息 - 由 {interaction.user} 清除")

    @clearMessages.error
    async def clearMessagesError(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.MissingAnyRole):
            await interaction.response.send_message("您沒有權限使用這個指令", ephemeral=True)
        elif isinstance(error, app_commands.CommandOnCooldown):
            timeRemaining = str(timedelta(
                seconds=int(error.retry_after)))
            await interaction.response.send_message(f"請等待 {timeRemaining} 秒後再執行指令", ephemeral=True)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Mod(bot), guilds=[testServerID])
