import os
from tortoise import Tortoise


async def connectToDatabase():
    await Tortoise.init(
        db_url=os.environ["DATABASE_URL"],
        modules={"models": ["apps.modules.users.schemas"]},
    )
