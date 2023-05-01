import asyncio

from arq import create_pool
from arq.connections import RedisSettings

from apps.libs import arq
from apps.libs.arq import worker


async def setup_arq():
    arq.pool_redis = await create_pool(RedisSettings())
    await worker.worker.main()


async def close_arq():
    asyncio.gather(arq.pool_redis.close(), worker.worker.close())
