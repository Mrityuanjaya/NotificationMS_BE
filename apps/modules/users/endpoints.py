from typing import List
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm

from apps.modules.users.services import UserServices
from apps.modules.users import (
    models as user_models,
    constants as user_constants,
    schemas as user_schemas,
)
from apps.modules.channels import services as channel_services
from apps.modules.common import auth, services as common_services
from apps.modules.jinja import setup as jinja_setup
from apps.libs import arq

router = APIRouter(tags=["users"])


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
    """
        checking if user has not accepted invitation then 
        he/she should not be able to login
    """
    if user.role == 2 and not await UserServices.invitation_accepted(user.id):
        raise HTTPException(
            status_code=400, detail=user_constants.INVITATION_NOT_ACCEPTED
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


@router.post("/invite", dependencies=[Depends(auth.is_system_admin)])
async def create_admin(request: Request, admin_data: user_models.AdminDataInput):
    user = await UserServices.get_user_by_email(admin_data.email)
    application = await UserServices.get_application_by_id(admin_data.application_id)

    if not application:
        raise HTTPException(
            status_code=404,
            detail=user_constants.ERROR_MESSAGES["APPLICATION_NOT_EXIST"],
        )
    system_channel = await channel_services.ChannelServices.get_active_channel_by_alias(
        "system channel"
    )
    if system_channel is None:
        raise HTTPException(
            status_code=404,
            detail=user_constants.ERROR_MESSAGES["CHANNEL_NOT_EXIST"],
        )
    email_conf = system_channel.configuration
    if not user:
        password = common_services.CommonServices.generate_unique_string(
            user_constants.PASSWORD_LENGTH
        )
        hashed_password = UserServices.get_password_hash(password)
        user = await user_schemas.User.create(
            name=admin_data.name,
            email=admin_data.email,
            hashed_password=hashed_password,
            role=2,
        )
        subject = "You are now an Admin"
        body = "Hi {}, here is your password for NotificationMS {}".format(
            admin_data.name, password
        )
        await arq.redis_pool.enqueue_job(
            "send_invitation", email_conf, admin_data.email, subject, body
        )

    admin = await UserServices.get_admin(user.id, admin_data.application_id)
    if admin:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=user_constants.ERROR_MESSAGES["USER_ALREADY_ADMIN"],
        )
    invitation_code = auth.create_access_token(
        data={"user_id": user.id, "application_id": application.id},
        expires_delta=timedelta(minutes=user_constants.INVITATION_TOKEN_EXPIRES_TIME),
    )
    await user_schemas.Admin.create(
        user_id=user.id,
        application_id=admin_data.application_id,
        status=1,
    )
    template_data = {
        "name": admin_data.name,
        "application": application.name,
        "invitationCode": invitation_code,
    }
    body = jinja_setup.find_template(request, "app", "invitation", template_data)
    await arq.redis_pool.enqueue_job(
        "send_invitation", email_conf, admin_data.email, "You are now an Admin", body
    )
    return {"Admin Created Successfully"}


@router.patch("/verify")
async def update_invitation_status(invitation_code: str):
    payload = auth.decode_access_token(invitation_code)
    admin = await UserServices.get_admin(
        payload.get("user_id"), payload.get("application_id")
    )
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Invalid Invitation Code"
        )
    if admin.status == 2:
        return user_constants.ALREADY_INVITED
    admin.status = 2
    await admin.save()
    return {"Invitation Accepted"}


@router.get(
    "/user/{user_id}",
    response_model=user_models.UserDataOutput,
    dependencies=[Depends(auth.is_system_admin)],
)
async def get_user(user_id: int):
    user = await UserServices.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=user_constants.USER_NOT_EXIST
        )
    return user


@router.get(
    "/admins",
    dependencies=[Depends(auth.is_system_admin)],
    response_model=user_models.AdminResponse,
)
async def get_all_admins(page_no: int = 1, records_per_page: int = 100):
    total_admins = await user_schemas.Admin.all().count()
    admins = (
        await user_schemas.Admin.filter(deleted_at = None)
        .limit(records_per_page)
        .offset(records_per_page * (page_no - 1))
        .prefetch_related("user", "application")
        .order_by("user__name")
    )
    admin_data = []
    for admin in admins:
        admin_data.append(
            {
                "user_id": admin.user_id,
                "application_id": admin.application_id,
                "email": admin.user.email,
                "name": admin.user.name,
                "application_name": admin.application.name,
                "status": str(admin.status).rsplit(".", 1)[1],
                "is_active": "True" if admin.deleted_at == None else "False",
            }
        )
    return {"total_admins": total_admins, "admins": admin_data}


@router.put("/user/{user_id}", dependencies=[Depends(auth.is_system_admin)])
async def update_admin_detail(user_id: int, admin_data: user_models.UserDataOutput):
    user = await UserServices.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="user not found"
        )

    user_with_email = await UserServices.get_user_by_email(admin_data.email.lower())
    if user_with_email and (user_with_email.id != user_id):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=user_constants.USER_ALREADY_EXIST,
        )

    user.name = admin_data.name
    user.email = admin_data.email
    user.role = admin_data.role
    await user.save()
    return {"User updated Successfully"}


@router.delete(
    "/user/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(auth.is_system_admin)],
)
async def delete_admin(user_id: int, application_id: int):
    admin = await UserServices.get_admin(user_id, application_id)
    if not admin:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No Admin Found"
        )
    admin.deleted_at = datetime.utcnow()
    await admin.save()
    return {"admin deleted successfully"}


@router.get("/validate_user")
async def validate_user(current_user: bool = Depends(auth.get_current_user)):
    if current_user == None:
        return {"loginStatus": False, "systemAdminStatus": False}
    if current_user.role == 1:
        return {"loginStatus": True, "systemAdminStatus": True}
    return {"loginStatus": True, "systemAdminStatus": False}
