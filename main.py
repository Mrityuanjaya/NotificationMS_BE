from fastapi import FastAPI
from tortoise import Tortoise
from dotenv import load_dotenv
from apps.core.db.config import connectToDatabase
from apps.modules.applications.endpoints import router as application_router


load_dotenv()
app = FastAPI()


@app.on_event("startup")
async def setup():
    await connectToDatabase()
    await Tortoise.generate_schemas()


app.include_router(application_router)
