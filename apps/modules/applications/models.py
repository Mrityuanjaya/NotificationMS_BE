from typing import List
from pydantic import BaseModel, Field


class ApplicationInput(BaseModel):
    name: str = Field(min_length=2) or Field(max_length=20)


class ApplicationOutput(ApplicationInput):
    id: int
    access_key: str = Field(max_length=64)


class Application(ApplicationInput):
    id: int


class ApplicationResponse(BaseModel):
    total_applications: int
    applications: List[Application]
