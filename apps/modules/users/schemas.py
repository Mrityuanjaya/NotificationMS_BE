from enum import IntEnum
from tortoise.models import Model
from tortoise import fields


class User(Model):
    class Role(IntEnum):
        SystemAdmin = 1
        Admin = 2

    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=255)
    email = fields.CharField(max_length=320)
    hashed_password = fields.CharField(max_length=64)
    role = fields.IntEnumField(Role)
    is_active = fields.BooleanField(default=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    modified_at = fields.DatetimeField(auto_now=True)
    deleted_at = fields.DatetimeField(null=True)


class Admin(Model):
    class Status(IntEnum):
        Invited = 1
        Accepted = 2

    user = fields.ForeignKeyField("models.User", related_name="users")
    application = fields.ForeignKeyField(
        "models.Application", related_name="applications"
    )
    status = fields.IntEnumField(Status)
    created_at = fields.DatetimeField(auto_now_add=True)
    modified_at = fields.DatetimeField(auto_now=True)
    deleted_at = fields.DatetimeField(null=True)

    class Meta:
        table = "admin"
        pk = ("user_id", "application_id")
