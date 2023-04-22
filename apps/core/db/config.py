import asyncio

from tortoise import Tortoise


async def setup(config):
    await asyncio.gather(Tortoise.init(config=config), Tortoise.generate_schemas())


async def close_connection():
    await Tortoise.close_connections()
