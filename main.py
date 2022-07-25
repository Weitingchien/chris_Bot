import os
import random
import asyncio
import aiohttp
from dotenv import load_dotenv
import discord
from discord.ext import commands, tasks
# scraoy
#from scrapy.proxy import sslProxies
from scrapy.ytNotification import ytNotification


# MongoDB
import motor.motor_asyncio

# MySQL
import pymysql

# Scheduler , timezone
import zoneinfo
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# Custom module
from event.signin import signin
from event.resetSignin import resetSignIn


load_dotenv()

hallChannelID = int(os.getenv("hallChannelID"))
testServerIDInt = int(os.getenv("testServerIDInt"))
testServerID = discord.Object(id=testServerIDInt)


class MyClient(commands.Bot):
    # initial_extensions = []  # class variable

    def __init__(self, intents):
        super().__init__(command_prefix="!", intents=intents,
                         application_id=os.getenv("applicationID"))
        self.initial_extensions = []
        # For storing user who sign-in in the server
        self.usersSignInTemp = []
        self.countOfReRequest = 0

    async def setup_hook(self) -> None:
        await self.backgroundTask()
        self.session = aiohttp.ClientSession()
        await self.load_cogs()
        await client.tree.sync(guild=testServerID)

    async def close(self):
        await super().close()
        await self.session.close()

    async def load_cogs(self) -> None:
        for filename in os.listdir("./cogs"):
            if filename.endswith(".py"):
                self.initial_extensions.append("cogs." + filename[:-3])

        for extension in self.initial_extensions:
            # discord.py version 2.0, Bot.load_extension is now a coroutine and has to be awaited
            await self.load_extension(extension)
            print(f"Loaded {extension}.")

    async def backgroundTask(self):
        print("Running background task")

        scheduler = AsyncIOScheduler(timezone="Asia/Taipei")

        async def checkTime():
            print("checkTime")
            channel = client.get_channel(hallChannelID)
            await channel.send("早安~~")

        async def reset(self):
            if(len(self.usersSignInTemp) == 0):
                self.usersSignInTemp.clear()
            await resetSignIn(self)

        scheduler.add_job(checkTime, "cron", hour=6,
                          minute=0, misfire_grace_time=60)

        scheduler.add_job(
            reset, "cron", [self], hour=0, minute=0, misfire_grace_time=60)  # misfire_grace_time  防止時間沒有剛好在整點執行 0:00:01.433713 最大誤差值允許為60秒

        scheduler.add_job(ytNotification, "interval", [
                          self], minutes=5, misfire_grace_time=240)

        scheduler.start()

    async def on_ready(self) -> None:
        print("on_ready")
        # Waiting for the bot to connect
        await self.wait_until_ready()
        # If found than return the guild
        guild = self.get_guild(testServerIDInt)
        print(guild)

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(send_messages=False)}
        videoCategoryName = "---youtube自動推播專區---"
        #announcement = "---公告區---"
        #annName = "重要公告"
        fpsName = "apex"
        await createCategory(self, guild, overwrites, videoCategoryName, announcement)

        videoCategory = discord.utils.get(
            guild.categories, name=videoCategoryName)

        apexChannel = discord.utils.get(guild.text_channels, name=fpsName)

        if apexChannel is None:
            print("創建Apex頻道 正在建立...")
            await guild.create_text_channel(fpsName, overwrites=overwrites, category=videoCategory)
            print("創建Apex頻道 建立成功...")

        print(
            f"Bot's name: {self.user.name} Version: { discord.__version__}")
        await self.change_presence(activity=discord.Game("-"))

    async def on_member_join(self, member) -> None:
        print(f"{member} has joined the server.")
        userAvatar = member.display_avatar
        channel = member.guild.system_channel
        embed = discord.Embed(title=f"Welcome", color=discord.Color.blue())
        embed.set_author(name=member.name, icon_url=userAvatar.url)
        embed.set_footer(
            text="joined_at: " + member.joined_at.strftime("%A, %B %d %Y @ %H:%M:%S %p"))
        await channel.send(embed=embed)

    async def on_member_remove(self, member):
        print(f"{member} has left the server.")

    async def on_message(self, message):
        print(f"user暫存資料: {self.usersSignInTemp}")
        if(message.author.bot):
            return

        for user in self.usersSignInTemp:
            if (user["_id"] == message.author.id):
                print("return")
                return

        userData = await signin(self, message)

        self.usersSignInTemp.append(
            {"_id": userData["_id"], "name": userData["name"], "signin": userData["signin"]})


async def createCategory(self, guild, overwrites, videoCategoryName, announcement) -> None:
    #print("---公告區--- 正在建立...")
    print("---youtube自動推播專區--- 正在建立...")
    #ann = discord.utils.get(guild.categories, name=announcement)
    video = discord.utils.get(guild.categories, name=videoCategoryName)
    #print(f"{ann} 先前已建立")
    print(f"{video} 先前已建立")
    """
    if ann is None:
        await guild.create_category(announcement)
        print("---公告區--- 建立成功")
    """
    if video is None:
        await guild.create_category(videoCategoryName)
        print("---youtube自動推播專區--- 建立成功")


intents = discord.Intents.default()
intents.members = True
client = MyClient(intents=intents)

# DB(MySQL) configuration
dbConfig = {
    "host": os.getenv("CLEARDB_HOST"),
    "port": int(os.getenv("CLEARDB_PORT")),
    "user": os.getenv("CLEARDB_USER"),
    "password": os.getenv("CLEARDB_DBPWD"),
    "db": os.getenv("CLEARDB_DB"),
    "charset": "utf8"
}


async def main(TOKEN):
    async with client:

        client.mongoConnect = motor.motor_asyncio.AsyncIOMotorClient(
            os.getenv("MONGODBCONNECTIONSTRING"))

        client.mysqlConnect = pymysql.connect(**dbConfig)
        await client.start(TOKEN)


if __name__ == '__main__':
    TOKEN = os.getenv("TOKEN")
    asyncio.run(main(TOKEN))
