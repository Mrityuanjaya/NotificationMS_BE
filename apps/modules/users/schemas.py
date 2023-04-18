from enum import IntEnum
from tortoise.models import Model
from tortoise import fields


class User(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=255)
    email = fields.CharField(max_length=320)
    is_active = fields.BooleanField(default=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    modified_at = fields.DatetimeField(auto_now=True)


class Admin(Model):
    class Role(IntEnum):
        SystemAdmin = 1
        Admin = 2

    class Status(IntEnum):
        Verified = 1
        NotVerified = 2
        Deleted = 3

    user = fields.ForeignKeyField("models.User", related_name="users")
    application = fields.ForeignKeyField(
        "models.Application", related_name="applications"
    )
    hashed_password = fields.CharField(max_length=64)
    role = fields.IntEnumField(Role)
    status = fields.IntEnumField(Status)
    created_at = fields.DatetimeField(auto_now_add=True)
    modified_at = fields.DatetimeField(auto_now=True)

    class Meta:
        table = "admin"
        pk = ("user_id", "application_id")
