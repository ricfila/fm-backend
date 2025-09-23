from tortoise import fields
from tortoise.models import Model


class User(Model):
    """
    The User model
    """

    id = fields.IntField(pk=True)
    username = fields.CharField(32, unique=True)
    password = fields.TextField()
    role = fields.ForeignKeyField(
        model_name="models.Role",
        default=2,
        on_delete=fields.SET_DEFAULT,
        on_update=fields.CASCADE
    )
    created_at = fields.DatetimeField(auto_now_add=True)

    role_id: int

    class Meta:
        table = "user"

    async def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "role_id": self.role_id,
            "created_at": self.created_at,
        }
