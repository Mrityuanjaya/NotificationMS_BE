from tortoise.models import Model
from tortoise import fields


class Application(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=200)
    access_key = fields.CharField(max_length=200)
    created_at = fields.DatetimeField(auto_now_add=True)
    modified_at = fields.DatetimeField(auto_now=True)
    deleted_at = fields.DatetimeField(null=True)
