import os
import random
from bs4 import BeautifulSoup
import asyncio
from pyppeteer import launch
#from scrapy.proxy import sslProxies


async def getApexChannelVideos(self):
    self.apexVideos = []
    db = self.mongoConnect["ytChannel"]
    collection = db["videos"]
    cursor = collection.find()
    async for document in cursor:
        apexVideos.append(document["videoTitle"])


async def getProxyList(self):
    cursor = self.mysqlConnect.cursor()
    sqlIps = "SELECT ip FROM ips"
    self.mysqlConnect.ping(reconnect=True)
    ips = cursor.execute(sqlIps)
    results = cursor.fetchall()
    proxyList = []
    for ip in results:
        proxyList.append(ip[0])
    return proxyList


async def parse(self, soup):
    videosTitle = soup.find(
        "h3", class_="ytd-grid-video-renderer").find("a", id="video-title").text

    print(videosTitle)

    videosLink = soup.find(
        "h3", class_="ytd-grid-video-renderer").find("a", id="video-title").get("href")

    print(videosLink)

    videosImage = soup.find("ytd-thumbnail", class_="ytd-grid-video-renderer").find(
        "yt-img-shadow", class_="ytd-thumbnail").find("img", id="img").get("src")
    print(videosImage)

    videosStatus = soup.find(
        "ytd-thumbnail-overlay-time-status-renderer", class_="ytd-thumbnail").get("overlay-style")
    print(videosStatus)

    videosChannelName = soup.find(
        "yt-formatted-string", class_="ytd-channel-name").text
    print(videosChannelName)

    videoLinkParse = str(videosLink).split("=", 1)
    videosID = videoLinkParse[1]

    print(videosID)

    videosViews = None
    videosUploadedTime = None

    for i, metadata in enumerate(soup.find("div", id="metadata-line").find_all("span")):
        if i == 0:
            videosViews = metadata.text
        elif i == 1:
            videosUploadedTime = metadata.text

    videoItem = {
        "videoID": videosID,
        "videoTitle": videosTitle,
        "videoLink": f"https://www.youtube.com{videosLink}",
        "videoImage": videosImage,
        "videoStatus": videosStatus,
        "videoViews": videosViews,
        "videoChannelName": videosChannelName,
        "videoUploadedTime": videosUploadedTime
    }
   # print(videoItem)
    await pipeLine(self, videoItem)


async def pipeLine(self, videoItem):
    db = self.mongoConnect["ytChannel"]
    collection = db["videos"]

    ifChannelNameDuplciated = await collection.find_one({"videoChannelName": videoItem["videoChannelName"]})

    if ifChannelNameDuplciated == None:
        if await collection.find_one({"videoID": videoItem["videoID"]}):
            print("video duplicated")
            return
        print("Insert NewData")
        await collection.insert_one(videoItem)
        channel = self.get_channel(
            int(os.getenv("apexChannelID")))  # Apex channel
        await channel.send(videoItem["videoLink"])
    elif ifChannelNameDuplciated != None:
        videoDupcliated = await collection.find_one({"$and": [{"videoChannelName": videoItem["videoChannelName"]}, {"videoID": {"$ne": videoItem["videoID"]}}]})
        if videoDupcliated == None:
            print("video duplicated")
            return
        print("video Updated")
        await collection.update_one({"videoChannelName": videoItem["videoChannelName"]}, {"$set": videoItem})
        channel = self.get_channel(
            int(os.getenv("apexChannelID")))  # Apex channel
        await channel.send(videoItem["videoLink"])


async def ytNotification(self):
    browser = await launch({"headless": True, "args": ["--disable-gpu", "--no-sandbox", "--disable--dev-shm-usage"]})
    page = await browser.newPage()

    urls = ["https://www.youtube.com/c/SellyTwitch/videos", "https://www.youtube.com/channel/UCVUmDq4aZ8_gzfCGiRO9KgA/videos",
            "https://www.youtube.com/channel/UCPwDQ6L9s6r1LDS753kpCHQ/videos", "https://www.youtube.com/channel/UCkiCNZ6c5Th3NpL2U8IhUWw/videos"]
    for url in urls:
        try:
            await page.goto(url)

            while not await page.querySelector("#continuations"):
                print("waitting...")
                pass

            pageSource = await page.content()
            soup = BeautifulSoup(pageSource, "html.parser")
            await asyncio.sleep(random.uniform(3, 5))
            await parse(self, soup)
        except Exception as e:
            print(e)
            await asyncio.sleep(random.uniform(3, 5))
            await browser.close()
    await asyncio.sleep(random.uniform(3, 5))
    await browser.close()
