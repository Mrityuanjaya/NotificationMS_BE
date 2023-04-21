from datetime import datetime, timedelta

from jose import jwt

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
