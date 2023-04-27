import asyncio
from arq import create_pool, Worker, jobs
from arq.connections import RedisSettings

from apps.libs.arq.worker import send_mail


async def end_job(ctx):
    id = ctx["job_id"]
    job = jobs.Job(id, ctx["redis"])
    job_data = await job.result_info()
    print(job_data)


worker = Worker(functions=[send_mail], after_job_end=end_job)


async def setup_arq():
    global redis_pool
    redis_pool = await create_pool(RedisSettings())
    asyncio.create_task(worker.main())


async def close_arq():
    await redis_pool.close()
    await worker.close()
