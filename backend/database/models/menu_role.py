from tortoise import fields
from tortoise.models import Model


class MenuRole(Model):
    """
    The MenuRole model
    """

    id = fields.IntField(pk=True)
    role = fields.ForeignKeyField(
        model_name="models.Role",
        on_delete=fields.RESTRICT,
        on_update=fields.CASCADE
    )
    menu = fields.ForeignKeyField(
        model_name="models.Menu",
        related_name="roles",
        on_delete=fields.CASCADE,
        on_update=fields.CASCADE
    )

    role_id: int
    menu_id: int

    class Meta:
        table = "menu_role"
        unique_together = ("role_id", "menu_id")

    async def to_dict(self):
        return {
            "id": self.id,
            "role_id": self.role_id,
            "menu_id": self.menu_id,
        }
