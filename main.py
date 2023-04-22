from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from tortoise import Tortoise

from apps.settings.local import settings
from apps.core.db import config as db_setup
from apps.modules.users.endpoints import router as user_router
from apps.modules.applications.endpoints import router as application_router
from apps.modules.recipients.endpoints import router as recipient_router

app = FastAPI()
app.include_router(user_router)
app.include_router(application_router)
app.include_router(recipient_router)
app.add_middleware(CORSMiddleware, **settings.CORS_CONFIG)



@app.on_event("startup")
async def on_startup():
    await db_setup.setup(settings.DATABASE_CONFIG)


@app.on_event("shutdown")
async def on_shutdown():
    await db_setup.close_connection()
