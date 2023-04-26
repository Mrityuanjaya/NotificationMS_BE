from enum import IntEnum
from tortoise import fields
from tortoise.models import Model
from apps.modules.common import schemas as common_schemas


class User(common_schemas.SoftDelete):
    class Role(IntEnum):
        SystemAdmin = 1
        Admin = 2

    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=255)
    email = fields.CharField(max_length=320)
    hashed_password = fields.CharField(max_length=64)
    role = fields.IntEnumField(Role)


class Admin(common_schemas.SoftDelete):
    class Status(IntEnum):
        Invited = 1
        Accepted = 2

    user = fields.ForeignKeyField("models.User", related_name="admins")
    application = fields.ForeignKeyField(
        "models.Application", related_name="admins"
    )
    status = fields.IntEnumField(Status)

    class Meta:
        table = "admin"
        pk = ("user_id", "application_id")

    