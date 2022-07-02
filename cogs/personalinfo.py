import os
import discord
from discord import app_commands
from discord.ext import commands
from db.fetchData import fetchData


testServerID = discord.Object(id=int(os.getenv("testServerIDInt")))


async def personalTemplate(bot, user):
    # print(user.id)
    userData, collection = await fetchData(bot, user)
    embed = discord.Embed(title=f"個人資料", color=discord.Color.blue())
    embed.set_author(name=user.name, icon_url=user.display_avatar)
    embed.add_field(name="存款", value=userData["coins"], inline=True)
    embed.add_field(name="今日簽到狀態",
                    value="已簽到" if userData["signin"] else "未簽到", inline=True)
    embed.add_field(name="帳號建立時間", value=userData["created_at"].strftime(
        "%Y/%m/%d - %H:%M:%S %p"), inline=False)
    """
    embed.set_footer(text="帳號建立時間" + userData["created_at"].strftime(
        "%Y/%m/%d - %H:%M:%S %p"))
    """
    return embed


class PersonalInfo(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="personalinfo", description="個人資訊")
    @app_commands.choices(choices=[app_commands.Choice(name="資料公開", value="on"), app_commands.Choice(name="資料不公開", value="off")])
    async def personalInfo(self, interaction: discord.Interaction, choices: app_commands.Choice[str]) -> None:
        if(choices.value == "on"):
            await interaction.response.send_message(embed=await personalTemplate(self.bot, interaction.user), ephemeral=False)
        else:
            await interaction.response.send_message(embed=await personalTemplate(self.bot, interaction.user), ephemeral=True)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(PersonalInfo(bot), guilds=[testServerID])
