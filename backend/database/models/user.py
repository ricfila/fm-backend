from tortoise import fields
from tortoise.models import Model


class User(Model):
    """
    The User model
    """

    id = fields.IntField(pk=True)
    username = fields.CharField(30, unique=True)
    password = fields.TextField()
    role = fields.ForeignKeyField("models.Role")

    class Meta:
        table = "user"

    async def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "role_id": self.role_id,
        }
