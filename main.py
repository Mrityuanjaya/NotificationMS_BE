from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from tortoise import Tortoise

from apps.settings.local import DATABASE_CONFIG, settings
from apps.core.db.config import connectToDatabase, disconnect
from apps.modules.users.endpoints import router as user_router
from apps.modules.applications.endpoints import router as application_router
from apps.modules.recipients.endpoints import router as recipients_router

app = FastAPI()

app.add_middleware(CORSMiddleware, **settings.CORS_CONFIG)



@app.on_event("startup")
async def onStartup():
    await connectToDatabase(DATABASE_CONFIG)
    await Tortoise.generate_schemas()


@app.on_event("shutdown")
async def onShutdown():
    await disconnect()


app.include_router(user_router)
app.include_router(application_router)
app.include_router(recipients_router)
