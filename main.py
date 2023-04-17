from fastapi import FastAPI
from tortoise import Tortoise

from apps.core.db.config import connectToDatabase

app = FastAPI()


@app.on_event("startup")
async def setup():
    await connectToDatabase()
    await Tortoise.generate_schemas()
