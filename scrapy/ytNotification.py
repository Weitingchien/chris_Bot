import os
import random
from bs4 import BeautifulSoup
import asyncio
from pyppeteer import launch
#from scrapy.proxy import sslProxies


"""
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
"""


async def getApexChannelVideos(self):
    self.apexVideos = []
    db = self.mongoConnect["ytChannel"]
    collection = db["ApexVideos"]
    cursor = collection.find()
    async for document in cursor:
        apexVideos.append(document["videoTitle"])


async def parse(self, soup, channelType):

    videosTitle = soup.find(
        "h3", class_="ytd-grid-video-renderer").find("a", id="video-title").text

    print(videosTitle)

    videosLink = soup.find(
        "h3", class_="ytd-grid-video-renderer").find("a", id="video-title").get("href")

    print(videosLink)

    videosStatus = soup.find(
        "ytd-thumbnail-overlay-time-status-renderer", class_="ytd-thumbnail").get("overlay-style")
    print(videosStatus)

    videosChannelName = soup.find(
        "yt-formatted-string", class_="ytd-channel-name").text
    print(videosChannelName)

    videosMetaData = soup.find("div", id="metadata-line").find_all("span")

    print(videosMetaData)

    videoLinkParse = None
    videosID = None

    if videosStatus != "SHORTS":
        videoLinkParse = str(videosLink).split("=", 1)
        videosID = videoLinkParse[1]
    else:
        videoLinkParse = str(videosLink).split("/", 2)
        videosID = videoLinkParse[2]

    print(videosID)

    videosViews = None
    videosUploadedTime = None

    for i, metadata in enumerate(videosMetaData):
        # VIDEO
        if len(videosMetaData) == 2:
            if i == 0:
                videosViews = metadata.text
            elif i == 1:
                videosUploadedTime = metadata.text
        # LIVE
        else:
            if i == 0:
                videosViews = metadata.text
            elif i == 1:
                videosUploadedTime = None

    videoItem = {
        "videoID": videosID,
        "videoTitle": videosTitle,
        "videoLink": f"https://www.youtube.com{videosLink}",
        "videoImage": None,
        "videoStatus": videosStatus,
        "videoViews": videosViews,
        "videoChannelName": videosChannelName,
        "videoUploadedTime": videosUploadedTime
    }
    await pipeLine(self, videoItem, channelType)
    return videosID


async def imageParse(self, soup, videoID, channelType):
    videosImage = soup.find("img").get("src")
    videoItem = {
        "videoImage": videosImage,
    }
    await imagePipeLine(self, videoItem, videoID, channelType)


async def pipeLine(self, videoItem, channelType):
    db = self.mongoConnect["ytChannel"]
    collection = None
    channel = None

    if channelType == "Apex":
        collection = db["ApexVideos"]
        channel = self.get_channel(int(os.getenv("apexChannelID")))

    elif channelType == "jTracks":
        collection = db["JTracksVideos"]
        channel = self.get_channel(int(os.getenv("jTracksChannelID")))

    ifChannelNameDuplciated = await collection.find_one({"videoChannelName": videoItem["videoChannelName"]})
    if ifChannelNameDuplciated == None:
        if await collection.find_one({"videoID": videoItem["videoID"]}):
            print("video duplicated")
            return
        print("Insert NewData")
        await collection.insert_one(videoItem)
        await channel.send(videoItem["videoLink"])
    elif ifChannelNameDuplciated != None:
        videoDupcliated = await collection.find_one({"$and": [{"videoChannelName": videoItem["videoChannelName"]}, {"videoID": {"$ne": videoItem["videoID"]}}]})
        if videoDupcliated == None:
            print("video duplicated")
            return
        print("video Updated")
        await collection.update_one({"videoChannelName": videoItem["videoChannelName"]}, {"$set": videoItem})
        await channel.send(videoItem["videoLink"])

    return videoItem["videoID"]


async def imagePipeLine(self, videoItem, videoID, channelType):
    db = self.mongoConnect["ytChannel"]
    collection = None

    if channelType == "Apex":
        collection = db["ApexVideos"]
    elif channelType == "jTracks":
        collection = db["JTracksVideos"]

    await collection.update_one({"videoID": videoID}, {"$set": videoItem})


async def ytNotification(self):
    browser = await launch({"headless": True, "args": ["--disable-gpu", "--no-sandbox", "--disable--dev-shm-usage"]})
    page = await browser.newPage()

    apexUrls = ["https://www.youtube.com/c/SellyTwitch/videos", "https://www.youtube.com/channel/UCVUmDq4aZ8_gzfCGiRO9KgA/videos",
                "https://www.youtube.com/channel/UCPwDQ6L9s6r1LDS753kpCHQ/videos", "https://www.youtube.com/channel/UCkiCNZ6c5Th3NpL2U8IhUWw/videos", "https://www.youtube.com/c/MoJoFPS/videos"]

    jTracksUrls = ["https://www.youtube.com/user/radwimpsstaff/videos", "https://www.youtube.com/c/Vaundy/videos", "https://www.youtube.com/c/kinggnuSMEJ/videos", "https://www.youtube.com/c/FujiiKaze/videos", "https://www.youtube.com/channel/UCpuMbQe3VhIpg22sbNbHQKQ/videos", "https://www.youtube.com/c/ooo0eve0ooo/videos", "https://www.youtube.com/c/harunoiswhoo/videos", "https://www.youtube.com/c/nbuna/videos", "https://www.youtube.com/channel/UC5e6XLQeSh1GM6phQX3u94Q/videos", "https://www.youtube.com/c/Islet/videos", "https://www.youtube.com/user/flumpoolchannel/videos", "https://www.youtube.com/c/backnumberchannel/videos", "https://www.youtube.com/user/sumikainc/videos", "https://www.youtube.com/c/hatamotohiro/videos",
                   "https://www.youtube.com/c/SHESChannel/videos", "https://www.youtube.com/c/miletOfficialYouTubeChannel/videos", "https://www.youtube.com/user/andropmusic/videos", "https://www.youtube.com/c/officialhigedandism/videos", "https://www.youtube.com/c/Mosawo7925/videos", "https://www.youtube.com/channel/UCBNVZPlWoR7oArfzJNrK9yw/videos", "https://www.youtube.com/channel/UC2iRI4qf-H_BdpsS8mMEjZQ/videos", "https://www.youtube.com/user/yasudareiSMEJ/videos", "https://www.youtube.com/c/Ado1024/videos", "https://www.youtube.com/channel/UClbieOB_NYcY9TlIthmyw-A/videos", "https://www.youtube.com/c/indigo_la_End/videos", "https://www.youtube.com/channel/UCtUcK6HrhD024CkPDsURBwg/videos"]

    videosIDAndChannelsType = []

    # Apex
    for url in apexUrls:
        try:
            await page.goto(url)

            while not await page.querySelector("#footer"):
                print("waitting...")
                pass

            pageSource = await page.content()
            soup = BeautifulSoup(pageSource, "html.parser")
            await asyncio.sleep(random.uniform(1, 3))
            videosIDAndChannelsType.append(f"{await parse(self, soup, 'Apex')}/Apex")
        except Exception as e:
            print(e)
            await asyncio.sleep(random.uniform(1, 3))
            await browser.close()

    # J-tracks
    for url in jTracksUrls:
        try:
            print(f"jTracks: {url}")
            await page.goto(url)

            while not await page.querySelector("#footer"):
                print("waitting...")
                pass

            pageSource = await page.content()
            soup = BeautifulSoup(pageSource, "html.parser")
            await asyncio.sleep(random.uniform(1, 3))
            videosIDAndChannelsType.append(f"{await parse(self, soup, 'jTracks')}/jTracks")
        except Exception as e:
            print(e)
            await asyncio.sleep(random.uniform(3, 5))
            await browser.close()

    for v in videosIDAndChannelsType:
        print(f"v: {v}")
        vParse = v.split('/')

        videoID = vParse[0]
        channelType = vParse[1]

        print("Searching Image")
        imagesUrl = f"https://i.ytimg.com/vi/{videoID}/hqdefault.jpg?"
        try:
            print(imagesUrl)
            await page.goto(imagesUrl)

            pageSource = await page.content()
            soup = BeautifulSoup(pageSource, "html.parser")
            await asyncio.sleep(random.uniform(1, 3))
            await imageParse(self, soup, videoID, channelType)
        except Exception as e:
            print(e)
            await asyncio.sleep(random.uniform(2, 4))
            await browser.close()

    await asyncio.sleep(random.uniform(3, 5))
    await browser.close()
