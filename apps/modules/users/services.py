from datetime import timedelta
from fastapi import HTTPException, status
from passlib.context import CryptContext

from apps.modules.users.schemas import User, Admin
from apps.modules.users.constants import ErrorMessages
from apps.modules.common.auth import create_access_token

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail=ErrorMessages.CREDENTIAL_EXCEPTION,
)


class UserCRUD:
    async def login(form_data):
        user = await User.filter(email=form_data.username).first()

        if user is None:
            raise credentials_exception

        admin = await Admin.filter(user_id=user.id).first()
        if not admin:
            raise credentials_exception

        if not verify_password(form_data.password, admin.hashed_password):
            raise credentials_exception

        access_token_expires = timedelta(minutes=120)
        access_token = create_access_token(
            data={"email": user.email}, expires_delta=access_token_expires
        )
        return {
            "access_token": access_token,
            "token_type": "bearer",
        }
