from db.fetchData import fetchData


async def signin(self, message):
    print("signin")
    userData, collection = await fetchData(self, message.author)
    if not(userData["signin"]):
        userData["signin"] = True
        await collection.replace_one({"_id": message.author.id}, userData)
    return userData
