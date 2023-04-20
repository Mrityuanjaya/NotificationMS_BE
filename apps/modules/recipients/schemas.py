from enum import IntEnum
from tortoise.models import Model
from tortoise import fields


class Recipient(Model):
    id = fields.IntField(pk=True)
    application = fields.ForeignKeyField("models.Application", related_name="applications")
    email = fields.CharField(max_length=320)
    created_at = fields.DatetimeField(auto_now=True)


class Device(Model):
    class Token_type(IntEnum):
        Push = 1
        Web = 2

    recipient = fields.ForeignKeyField("models.Recipient", related_name="devices")
    token = fields.CharField(max_length=255)
    token_type = fields.IntField(Token_type)