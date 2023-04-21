from enum import IntEnum
from tortoise import fields

from apps.modules.common import schemas as common_schemas


class User(common_schemas.softDelete):
    class Role(IntEnum):
        SystemAdmin = 1
        Admin = 2

    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=200)
    email = fields.CharField(max_length=320)
    hashed_password = fields.CharField(max_length=64)
    role = fields.IntEnumField(Role)


class Admin(common_schemas.softDelete):
    user = fields.ForeignKeyField("models.User", related_name="users", pk=True)
