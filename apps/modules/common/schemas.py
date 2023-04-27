from tortoise.models import Model
from tortoise import fields


class Base(Model):
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        abstract = True


class Update(Base):
    modified_at = fields.DatetimeField(auto_now=True)

    class Meta:
        abstract = True


class softDelete(Update):
    deleted_at = fields.DatetimeField(null=True)

    class Meta:
        abstract = True
