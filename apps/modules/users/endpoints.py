from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from apps.modules.common.auth import get_current_user, is_system_admin

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
    return await UserServices.update_invitation_status(invitation_code)


@router.get("/validate_user")
async def validate_user(current_user: bool = Depends(get_current_user)):
    if current_user == None: 
        return {"loginStatus":False, "systemAdminStatus": False}
    if current_user.role == 1:
        return {"loginStatus": True, "systemAdminStatus": True}
    return {"loginStatus": True, "systemAdminStatus": False}
    