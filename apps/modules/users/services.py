from passlib.context import CryptContext
from pydantic import EmailStr
from apps.modules.users import schemas as user_schemas


class UserServices:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def verify_password(plain_password, hashed_password):
        return UserServices.pwd_context.verify(plain_password, hashed_password)

    async def get_user_by_email(email) -> user_schemas.User:
        user = await user_schemas.User.filter(email=email).first()
        return user
