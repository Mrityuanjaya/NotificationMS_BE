from enum import IntEnum
from tortoise import fields

from apps.modules.common import schemas as common_schemas


class Notification(common_schemas.Base):
    id = fields.UUIDField(pk=True)
    request = fields.ForeignKeyField("models.Request", related_name="notifications")
    recipients = fields.ForeignKeyField(
        "models.Recipient", related_name="notifications"
    )
    status = fields.BooleanField(default=False)


class Request(common_schemas.Base):
    class Priority(IntEnum):
        EMAIL_PUSH_WEB = 1
        EMAIL_PUSH = 2
        EMAIL = 3

    id = fields.UUIDField(pk=True)
    application = fields.ForeignKeyField("models.Application", related_name="requests")
    body = fields.JSONField()
    template = fields.CharField() | None
    total_request = fields.IntField()
    priority = fields.IntField(Priority)
    response = fields.JSONField()
