from datetime import timedelta
from fastapi import HTTPException, status
from passlib.context import CryptContext

from apps.modules.users.schemas import User, Admin
from apps.modules.users.constants import ERROR_MESSAGES, TOKEN_EXPIRY_MINUTES
from apps.modules.common.auth import create_access_token


class UserServices:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def verify_password(plain_password, hashed_password):
        return UserServices.pwd_context.verify(plain_password, hashed_password)

    async def login(form_data):
        user = await User.filter(email=form_data.username).first()

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=ERROR_MESSAGES["CREDENTIAL_EXCEPTION"],
            )

        admin = await Admin.filter(user_id=user.id).first()
        if not admin:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=ERROR_MESSAGES["CREDENTIAL_EXCEPTION"],
            )

        if not UserServices.verify_password(form_data.password, admin.hashed_password):
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
            "token_type": "bearer",
        }
