from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from tortoise import Tortoise
from dotenv import load_dotenv
from apps.settings.local import settings
from apps.core.db.config import connectToDatabase, disconnect
from apps.modules.users.endpoints import router as user_router

from apps.modules.applications.endpoints import router as application_router


load_dotenv()
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


app.include_router(application_router)
