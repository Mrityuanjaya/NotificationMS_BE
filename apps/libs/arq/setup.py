import asyncio

from arq import create_pool
from arq.connections import RedisSettings

from apps.libs import arq
from apps.libs.arq import worker


async def setup_arq():
    arq.broker = await create_pool(RedisSettings())
    await worker.worker.main()


async def close_arq():
    asyncio.gather(arq.broker.close(), worker.worker.close())
