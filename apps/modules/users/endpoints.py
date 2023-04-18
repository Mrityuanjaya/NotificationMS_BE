from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from apps.modules.users.services import UserServices
from apps.modules.users.models import Login

router = APIRouter()


@router.post("/login", response_model=Login)
async def login(form_data: OAuth2PasswordRequestForm = Depends()) -> Login:
    return await UserServices.login(form_data)
