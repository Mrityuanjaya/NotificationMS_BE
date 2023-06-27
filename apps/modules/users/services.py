from passlib.context import CryptContext

from apps.modules.users import schemas as user_schemas
from apps.modules.applications import schemas as application_schemas


class UserServices:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def verify_password(plain_password, hashed_password):
        return UserServices.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(password):
        print(UserServices.pwd_context.hash(password))
        return UserServices.pwd_context.hash(password)

    async def get_user_by_email(email) -> user_schemas.User:
        user = await user_schemas.User.filter(email=email).first()
        return user

    async def get_user_by_id(id) -> user_schemas.User:
        user = await user_schemas.User.filter(id=id).first()
        return user

    async def get_application_by_id(id: int) -> application_schemas.Application:
        application = await application_schemas.Application.filter(id=id).first()
        return application

    async def get_admin(user_id: int, application_id: int) -> user_schemas.Admin:
        admin = await user_schemas.Admin.filter(
            user_id=user_id, application_id=application_id, deleted_at=None
        ).first()
        return admin

    async def invitation_accepted(user_id: int):
        admin = await user_schemas.Admin.filter(
            user_id=user_id, status=2, deleted_at__isnull=True
        ).first()
        if not admin:
            return False
        return True

    async def get_active_application_ids_by_admin_id(admin_id: int):
        admin_instances = (
            await user_schemas.Admin.filter(user_id=admin_id, deleted_at__isnull=True)
            .order_by("created_at")
            .values("application_id")
        )                   # valuesList
        application_ids = []  # List Comprehension
        for admin_instance in admin_instances:
            application_ids.append(admin_instance["application_id"])
        return application_ids
