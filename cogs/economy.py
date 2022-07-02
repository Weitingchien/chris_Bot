import os
import discord
from discord import app_commands
from discord.ext import commands
from db.fetchData import fetchData
from datetime import timedelta
import time
import random


testServerID = discord.Object(id=int(os.getenv("testServerIDInt")))


class Economy(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.checks.cooldown(1, 86400.0, key=lambda i: (i.guild_id, i.user.id))
    @app_commands.command(name="gamble", description="使用一次指令可獲得1~50幣(隨機),冷卻時間為一天")
    async def gamble(self, interaction: discord.Interaction) -> None:

        userData, collection = await fetchData(self.bot, interaction.user)

        getMoney = random.randint(1, 50)
        userData["coins"] += getMoney
        await collection.replace_one({"_id": interaction.user.id}, userData)
        await interaction.response.send_message(f"你獲得 {getMoney} 幣!", ephemeral=True)

    @gamble.error
    async def gambleError(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.CommandOnCooldown):
            timeRemaining = str(timedelta(
                seconds=int(error.retry_after)))
            embed = discord.Embed(
                description=f"請等待 {timeRemaining} 秒後再執行指令", color=0xe74c3c)
            await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Economy(bot), guilds=[testServerID])
