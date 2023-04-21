from pydantic import BaseModel
from pydantic import Field


class ApplicationInput(BaseModel):
    name: str = Field(min_length=2) or Field(max_length=20)


class ApplicationOutput(ApplicationInput):
    id: int
    access_key: str = Field(max_length=64)


class Application(BaseModel):
    id: int
    name: str = Field(min_length=2) or Field(max_length=20)
