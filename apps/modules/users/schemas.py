from enum import IntEnum
from tortoise.models import Model
from tortoise import fields


class Role(IntEnum):
    SystemAdmin = 1
    Admin = 2


class User(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=200)
    email = fields.CharField(max_length=320)
    is_active = fields.BooleanField(default=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    modified_at = fields.DatetimeField(auto_now=True)


class Admin(Model):
    user = fields.ForeignKeyField("models.User", related_name="users", pk=True)
    hashed_password = fields.CharField(max_length=64)
    role = fields.IntEnumField(Role)
