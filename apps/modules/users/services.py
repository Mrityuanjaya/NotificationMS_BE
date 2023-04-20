from datetime import timedelta
from fastapi import HTTPException, status
from fastapi_mail import FastMail, MessageSchema
from passlib.context import CryptContext
from jinja2 import Environment, FileSystemLoader

from apps.modules.users.schemas import User, Admin
from apps.modules.applications.schemas import Application
from apps.modules.users.models import Login, AdminDataInput
from apps.modules.users.constants import (
    ERROR_MESSAGES,
    TOKEN_EXPIRY_MINUTES,
    PASSWORD_LENGTH,
    INVITATION_CODE_LENGTH,
)
from apps.modules.common.services import CommonServices
from apps.modules.common.auth import create_access_token
from apps.settings.local import settings

env = Environment(loader=FileSystemLoader("apps/templates/app"))
template = env.get_template("invitation.html")


class UserServices:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def verify_password(plain_password, hashed_password):
        return UserServices.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(password):
        return UserServices.pwd_context.hash(password)

    async def login(form_data) -> Login:
        user = await User.filter(email=form_data.username).first()

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=ERROR_MESSAGES["CREDENTIAL_EXCEPTION"],
            )
        if not UserServices.verify_password(form_data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=ERROR_MESSAGES["CREDENTIAL_EXCEPTION"],
            )

        access_token_expires = timedelta(TOKEN_EXPIRY_MINUTES)
        access_token = create_access_token(
            data={"email": user.email}, expires_delta=access_token_expires
        )
        return {
            "access_token": access_token,
            "role": user.role,
            "token_type": "bearer",
        }

    async def create_admin(admin_data: AdminDataInput):
        user = await User.filter(email=admin_data.email).first()
        application = await Application.filter(id=admin_data.application_id).first()

        if not application:
            raise HTTPException(
                status_code=404, detail="This application doesn't exist"
            )

        if not user:
            password = CommonServices.generate_unique_string(PASSWORD_LENGTH)
            hashed_password = UserServices.get_password_hash(password)
            user = await User.create(
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

        admin = await Admin.filter(
            user_id=user.id, application_id=admin_data.application_id
        ).first()
        if admin:
            raise HTTPException(
                status_code=403, detail="User is already a admin of this application"
            )
        if not admin:
            invitation_code = CommonServices.generate_unique_string(
                INVITATION_CODE_LENGTH
            )
            await Admin.create(
                user_id=user.id,
                application_id=admin_data.application_id,
                status=1,
                invitation_code=invitation_code,
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
        admin = await Admin.filter(invitation_code=invitation_code).first()
        if not admin:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Invalid Code"
            )
        admin.status = 2
        await admin.save()
        return {"Invitation Accepted"}
