from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from apps.modules.users.services import UserCRUD

router = APIRouter()


@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    return await UserCRUD.login(form_data)
