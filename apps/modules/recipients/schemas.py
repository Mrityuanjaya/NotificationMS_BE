from enum import IntEnum
from tortoise.models import Model
from tortoise import fields


class Recipient(Model):
    id = fields.UUIDField(pk=True)
    application = fields.ForeignKeyField(
        "models.Application", related_name="recipients"
    )
    email = fields.CharField(max_length=320)
    created_at = fields.DatetimeField(auto_now=True)


class Device(Model):
    class Token_type(IntEnum):
        Push = 1
        Web = 2

    id = fields.UUIDField(pk=True)
    recipient = fields.ForeignKeyField("models.Recipient", related_name="devices")
    token = fields.CharField(max_length=255)
    token_type = fields.IntEnumField(enum_type=Token_type)
