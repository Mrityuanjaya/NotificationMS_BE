from pydantic import BaseModel, EmailStr


class Login(BaseModel):
    access_token: str
    role: int
    token_type: str


class AdminDataInput(BaseModel):
    name: str
    email: EmailStr
    application_id: int
