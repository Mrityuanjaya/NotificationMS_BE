from tortoise.models import Model
from tortoise import fields


class Base(Model):
    created_at = fields.DatetimeField(auto_now_add=True)
    modified_at = fields.DatetimeField(auto_now=True)

    class Meta:
        abstract = True


class SoftDelete(Base):
    deleted_at = fields.DatetimeField(null=True)

    class Meta:
        abstract = True
