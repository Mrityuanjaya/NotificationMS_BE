from tortoise import Tortoise


async def connectToDatabase(config):
    await Tortoise.init(config=config)


async def disconnect():
    await Tortoise.close_connections()
