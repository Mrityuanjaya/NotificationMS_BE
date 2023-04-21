from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from apps.modules.users.services import UserServices
from apps.modules.users import models as user_models, constants as user_constants
from apps.modules.common import auth

router = APIRouter()


@router.post("/login", response_model=user_models.Login)
async def login(form_data: OAuth2PasswordRequestForm = Depends()) -> user_models.Login:
    try:
        login_data = user_models.LoginEmail(email=form_data.username)
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please Enter valid Email address",
        )
    user = await UserServices.get_user_by_email(login_data.email)
    if user is None or not UserServices.verify_password(
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
