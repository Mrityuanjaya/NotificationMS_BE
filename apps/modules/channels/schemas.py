from tortoise import fields, exceptions
from enum import IntEnum
from apps.modules.common import schemas as common_schemas
from apps.modules.channels import constants as channel_constants

class Channel(common_schemas.SoftDelete):
    class ChannelType(IntEnum):
        Email= 1
        Push= 2
        Web= 3


    alias = fields.CharField(max_length=255, pk=True)
    application = fields.ForeignKeyField("models.Application", related_name="channels")
    name = fields.CharField(max_length=255)
    description = fields.CharField(max_length=255)
    type = fields.IntEnumField(ChannelType)
    type = fields.IntEnumField(ChannelType)
    configuration = fields.JSONField()


    async def save(self, *args, **kwargs):
        if self.type == channel_constants.EMAIL_CHANNEL_TYPE:
            allowed_keys = ["email", "password", "mail_from", "mail_port", "mail_server", "use_credentials", "mail_starttls", "mail_ssl_tls"]
        else:
            allowed_keys = ["api_key", "auth_domain", "project_id", "storage_bucket", "messaging_sender_id", "app_id", "measurement_id"]
        disallowed_keys = set(self.configuration.keys()) - set(allowed_keys)
        if disallowed_keys:
            raise exceptions.ValidationError(f"Invalid keys: {disallowed_keys}")
        return await super().save(*args, **kwargs)

