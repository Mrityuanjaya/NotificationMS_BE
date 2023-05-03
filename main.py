import asyncio

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from apps.settings.local import settings
from apps.core.db import config as db_setup
from apps.modules.users.endpoints import router as user_router
from apps.modules.applications.endpoints import router as application_router
from apps.modules.notifications.endpoints import router as notification_router
from apps.modules.recipients.endpoints import router as recipient_router
from apps.libs.arq import setup as arq_setup

from apps.modules.channels.endpoints import router as channel_router

app = FastAPI()
app.mount(
    "/apps/modules/jinja/static",
    StaticFiles(directory="apps/modules/jinja/static"),
    name="static",
)
app.include_router(user_router)
app.include_router(application_router)
app.include_router(recipient_router)
app.include_router(notification_router)
app.include_router(channel_router)
app.add_middleware(CORSMiddleware, **settings.CORS_CONFIG)


@app.on_event("startup")
async def on_startup():
    asyncio.gather(db_setup.setup(settings.DATABASE_CONFIG), arq_setup.setup_arq())


@app.on_event("shutdown")
async def on_shutdown():
    asyncio.gather(db_setup.close_connection(), arq_setup.close_arq())
