async def fetchData(bot, user):
    print("fetchData")
    db = bot.mongoConnect["chrisbotdb"]
    collection = db["chrisboteconomy"]
    if await collection.find_one({"_id": user.id}) == None:
        newData = {
            "_id": user.id,
            "name": user.name,
            "coins": 0,
            "signin": False,
            "created_at": user.created_at
        }
        await collection.insert_one(newData)
    return await collection.find_one({"_id": user.id}), collection
