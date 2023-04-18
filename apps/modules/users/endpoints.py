from typing import Annotated
from fastapi import APIRouter, Depends, Header
from fastapi.security import OAuth2PasswordRequestForm

from apps.modules.users.services import UserCRUD

router = APIRouter()


@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    return await UserCRUD.login(form_data)

@router.get("/validate_system_admin")
async def validate_system_admin(token: Annotated[str | None, Header()] = None):
    email = UserCRUD.get_email_from_token(token)
    return await UserCRUD.get_system_admin_status(email)