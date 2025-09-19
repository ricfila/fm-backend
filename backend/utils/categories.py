from backend.database.models import Category
from backend.models.error import Conflict
from backend.utils import ErrorCodes


async def check_cyclic_links(
        category_id: int,
        parent_category: Category, 
        type_of_parent: str
    ):
    while parent_category is not None:
        if parent_category.id == category_id:
            raise Conflict(
                message="Impossibile impostare un collegamento ciclico",
                code=ErrorCodes.CYCLIC_LINK_OF_CATEGORIES)

        parent_category = await getattr(parent_category, type_of_parent)
