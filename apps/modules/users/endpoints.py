from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from apps.modules.common.auth import get_current_user, is_system_admin
from apps.modules.users import services as user_services
from apps.modules.users import models as user_models, constants as user_constants
from apps.modules.common import auth
from apps.modules.users.models import Login, AdminDataInput

router = APIRouter()


@router.post("/login", response_model=user_models.Login)
async def login(form_data: OAuth2PasswordRequestForm = Depends()) -> Login:
    try:
        login_data = user_models.LoginEmail(email=form_data.username)
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please Enter valid Email address",
        )
    user = await user_services.UserServices.get_user_by_email(login_data.email)
    if user is None or not user_services.UserServices.verify_password(
        form_data.password, user.hashed_password
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=user_constants.ERROR_MESSAGES["CREDENTIAL_EXCEPTION"],
        )
    access_token_expires = timedelta(minutes=user_constants.TOKEN_EXPIRY_MINUTES)
    access_token = auth.create_access_token(
        data={"email": user.email}, expires_delta=access_token_expires
    )
    return {
        "access_token": access_token,
        "role": user.role,
        "token_type": user_constants.TOKEN_TYPE,
    }


@router.post("/invite", dependencies=[Depends(is_system_admin)])
async def create_admin(admin_data: AdminDataInput):
    return await user_services.UserServices.create_admin(admin_data)


@router.patch("/verify")
async def update_invitation_status(invitation_code: str):
    return await user_services.UserServices.update_invitation_status(invitation_code)


@router.get("/validate_user")
async def validate_user(current_user: bool = Depends(get_current_user)):
    if current_user == None: 
        return {"loginStatus":False, "systemAdminStatus": False}
    if current_user.role == 1:
        return {"loginStatus": True, "systemAdminStatus": True}
    return {"loginStatus": True, "systemAdminStatus": False}
    