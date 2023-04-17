from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from tortoise import Tortoise

from apps.core.db.config import connectToDatabase
from apps.modules.users.endpoints import router as user_router

load_dotenv()

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def setup():
    await connectToDatabase()
    await Tortoise.generate_schemas()


app.include_router(user_router)
