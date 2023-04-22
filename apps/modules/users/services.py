from datetime import timedelta
from fastapi import HTTPException, status
from fastapi_mail import MessageSchema
from passlib.context import CryptContext
from pydantic import EmailStr
from apps.modules.users import schemas as user_schemas, models as user_models
from jinja2 import Environment, FileSystemLoader

from apps.modules.users.constants import (
    ERROR_MESSAGES,
    TOKEN_EXPIRY_MINUTES,
    PASSWORD_LENGTH,
    INVITATION_TOKEN_EXPIRES_TIME,
)
from apps.modules.common.services import CommonServices
from apps.modules.common.auth import create_access_token, decode_access_token
from apps.settings.local import settings
from apps.modules.applications import models as application_models, schemas as application_schemas
env = Environment(loader=FileSystemLoader("apps/templates/app"))
template = env.get_template("invitation.html")


class UserServices:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def verify_password(plain_password, hashed_password):
        return UserServices.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(password):
        return UserServices.pwd_context.hash(password)
    
    async def get_user_by_email(email) -> user_schemas.User:
        user = await user_schemas.User.filter(email=email).first()
        return user

    async def create_admin(admin_data: user_models.AdminDataInput):
        user = await user_schemas.User.filter(email=admin_data.email).first()
        application = await application_schemas.Application.filter(id=admin_data.application_id).first()

        if not application:
            raise HTTPException(
                status_code=404, detail=ERROR_MESSAGES["APPLICATION_NOT_EXIST"]
            )

        if not user:
            password = CommonServices.generate_unique_string(PASSWORD_LENGTH)
            hashed_password = UserServices.get_password_hash(password)
            user = await user_schemas.User.create(
                name=admin_data.name,
                email=admin_data.email,
                hashed_password=hashed_password,
                role=2,
            )
            message = MessageSchema(
                subject="You are now an Admin",
                recipients=[admin_data.email],
                body="Hi {}, here is your password for NotificationMS {}".format(
                    admin_data.name, password
                ),
                subtype="html",
            )
            await settings.SEND_MAIL.send_message(message)

        admin = await user_schemas.Admin.filter(
            user_id=user.id, application_id=admin_data.application_id
        ).first()
        if admin:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ERROR_MESSAGES["USER_ALREADY_ADMIN"],
            )
        if not admin:
            invitation_code = create_access_token(
                data={"user_id": user.id, "application_id": application.id},
                expires_delta=timedelta(INVITATION_TOKEN_EXPIRES_TIME),
            )
            await user_schemas.Admin.create(
                user_id=user.id,
                application_id=admin_data.application_id,
                status=1,
            )
            output = template.render(
                name=admin_data.name,
                application=application.name,
                invitationCode=invitation_code,
            )
            message = MessageSchema(
                subject="You are now an Admin",
                recipients=[admin_data.email],
                body=output,
                subtype="html",
            )
            await settings.SEND_MAIL.send_message(message)
        return {"Admin Created Successfully"}

    async def update_invitation_status(invitation_code: str):
        payload = decode_access_token(invitation_code)
        admin = await user_schemas.Admin.filter(
            user_id=payload.get("user_id"), application_id=payload.get("application_id")
        ).first()
        if not admin:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Invalid Invitation Code"
            )
        if admin.status == 2:
            return {"Invitation already Accepted"}
        admin.status = 2
        await admin.save()
        return {"Invitation Accepted"}
