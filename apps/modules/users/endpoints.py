from typing import Annotated
from fastapi import APIRouter, Depends, Header
from fastapi.security import OAuth2PasswordRequestForm
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from apps.modules.common.auth import is_system_admin

from apps.modules.common.auth import is_system_admin
from apps.modules.users.services import UserServices
from apps.modules.users.models import Login, AdminDataInput

router = APIRouter()


@router.post("/login", response_model=Login)
async def login(form_data: OAuth2PasswordRequestForm = Depends()) -> Login:
    return await UserServices.login(form_data)


@router.post("/invite", dependencies=[Depends(is_system_admin)])
async def create_admin(admin_data: AdminDataInput):
    return await UserServices.create_admin(admin_data)


@router.patch("/verify")
async def update_invitation_status(invitation_code: str):
    print(invitation_code)
    return await UserServices.update_invitation_status(invitation_code)


@router.get("/validate_system_admin")
async def validate_system_admin(is_system_admin: bool = Depends(is_system_admin)):
    return is_system_admin
