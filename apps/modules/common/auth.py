from fastapi import status
from fastapi import HTTPException
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime, timedelta
from jose import JWTError, jwt

from apps.modules.users.schemas import Admin, User
from apps.modules.common.constants import ERROR_MESSAGES
from apps.settings.local import settings


def create_access_token(data: dict, expires_delta: timedelta) -> jwt:
    """
    function to generate a jwt token when a user logs in.
    token will encode user's email inside it
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def decode_access_token(token: str):
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=ERROR_MESSAGES["INVALID_CREDENTIALS"],
        )


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
):
    """
    function to get the current user
    """
    payload = decode_access_token(token)
    email: str = payload.get("email")
    if email is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=ERROR_MESSAGES["INVALID_CREDENTIALS"],
        )
    user = await User.filter(email=email).first()
    return user


async def is_system_admin(current_user=Depends(get_current_user)):
    """
    function to check if the current user is System Admin or not
    """
    return current_user.role == 1
