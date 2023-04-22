from tortoise.models import Model
from tortoise import fields

from apps.modules.common import schemas as common_schemas


class Application(common_schemas.softDelete):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=255)
    access_key = fields.CharField(max_length=255)
