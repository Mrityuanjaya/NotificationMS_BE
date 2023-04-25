from pydantic import BaseModel
from pydantic import Field, validator, EmailStr


class LoginEmail(BaseModel):
    email: EmailStr


class Login(BaseModel):
    access_token: str
    role: int
    token_type: str


class UserData(BaseModel):
    name: str = Field(min_length=3) or Field(max_length=255)
    email: EmailStr

    @validator("email")
    def check_email_max_length(cls, v):
        if len(v) > 320:
            raise ValueError("email must be no more than 50 characters")
        return v


class UserDataOutput(UserData):
    role: int


class AdminDataInput(UserData):
    application_id: int


class AdminDataOutput(UserData):
    application_name: str
    status: str
    is_active: str
    application_id: int
    user_id: int
