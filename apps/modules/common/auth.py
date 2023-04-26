from fastapi import status
from fastapi import HTTPException
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime, timedelta
from jose import JWTError, jwt, ExpiredSignatureError

from apps.modules.users import schemas as user_schemas
from apps.modules.common import constants as common_constants
from apps.settings.local import settings


def create_access_token(data: dict, expires_delta: timedelta) -> jwt:
    """
    function to generate a jwt token when a user logs in.
    token will encode user's email inside it
    """
    expiry_time = datetime.utcnow() + expires_delta
    data.update({"exp": expiry_time})
    encoded_jwt = jwt.encode(data, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str):
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        return payload
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=common_constants.ERROR_MESSAGES["TOKEN_EXPIRED"],
        )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=common_constants.ERROR_MESSAGES["INVALID_CREDENTIALS"],
        )


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
) -> user_schemas.User:
    """
    function to get the current user
    """
    payload = decode_access_token(token)
    email: str = payload.get("email")
    if email is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=common_constants.ERROR_MESSAGES["INVALID_CREDENTIALS"],
        )
    user = await user_schemas.User.filter(email=email).first()
    return user


async def is_system_admin(current_user: user_schemas.User = Depends(get_current_user)):
    """
    function check if the current user is System Admin or not
    """
    if current_user.role != 1:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=common_constants.ERROR_MESSAGES["FORBIDDEN_USER"])