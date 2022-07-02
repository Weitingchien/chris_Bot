import os
import discord
from discord import app_commands
from discord.ext import commands


testServerID = discord.Object(id=int(os.getenv("testServerIDInt")))


class Help(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.commands = {"gamble":  "使用一次指令可獲得1~50幣 冷卻時間為一天",
                         "personalinfo": "個人資訊 顯示時可設公開或不公開", "help": "顯示所有可用指令"}

    @app_commands.command(name="help", description="顯示所有可用指令")
    async def help(self, interaction: discord.Interaction) -> None:

        embed = discord.Embed(
            title="指令", color=discord.Color.from_rgb(66, 185, 131))

        for key, value in self.commands.items():
            embed.add_field(name=key, value=value, inline=False)

        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(Help(bot), guilds=[testServerID])
