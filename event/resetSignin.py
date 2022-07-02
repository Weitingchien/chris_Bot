async def resetSignIn(bot):
    print("簽到重置")
    db = bot.mongoConnect["chrisbotdb"]
    collection = db["chrisboteconomy"]
    await collection.update_many({"signin": True}, {"$set": {"signin": False}})
