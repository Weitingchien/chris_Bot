import os
import discord
from discord import app_commands
from discord.ext import commands


testServerID = discord.Object(id=int(os.getenv("testServerIDInt")))


class Ping(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    """
    @commands.Cog.listener()
    async def on_ready(self):
        await self.bot.change_presence(activity=discord.Game("Im online"))
    """
    @app_commands.command(name="ping", description="ping")
    async def ping(self, interaction: discord.Interaction) -> None:
        await interaction.response.send_message(f"The current latency of the bot is {round(self.bot.latency * 1000, 1)}ms.", ephemeral=True)

# export this cog


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Ping(bot), guilds=[testServerID])
