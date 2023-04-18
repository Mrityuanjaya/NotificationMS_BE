from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from tortoise import Tortoise

from apps.settings.local import settings
from apps.core.db.config import connectToDatabase, disconnect
from apps.modules.users.endpoints import router as user_router


app = FastAPI()
app.add_middleware(CORSMiddleware, **settings.CORS_CONFIG)

origins = ["*"]


@app.on_event("startup")
async def onStartup():
    await connectToDatabase(settings.DATABASE_CONFIG)
    await Tortoise.generate_schemas()


@app.on_event("shutdown")
async def onShutdown():
    await disconnect()


app.include_router(user_router)
