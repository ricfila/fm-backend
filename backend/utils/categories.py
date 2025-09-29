from backend.database.models import Category
from backend.models.error import Conflict, NotFound
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


async def collapseCategories(categories, parent_field, connection):
    new_categories = []

    for c in categories:
        parent_id = getattr(c, parent_field)

        if parent_id is not None:
            if not any(k.id == parent_id for k in categories + new_categories):
                new_c = await Category.get_or_none(id=parent_id, using_db=connection)
                if not new_c:
                    raise NotFound(ErrorCodes.CATEGORY_NOT_FOUND)
                new_categories.append(new_c)
        
        else:
            new_categories.append(c)
    
    return new_categories


async def collapseOrphanCategories(categories, parent_field, connection):
    new_categories = []

    for c in categories:
        parent_id = getattr(c, parent_field)

        if parent_id is not None:
            if not any(k.id == parent_id for k in categories + new_categories):
                new_c = await Category.get_or_none(id=parent_id, using_db=connection)
                if not new_c:
                    raise NotFound(ErrorCodes.CATEGORY_NOT_FOUND)
                new_categories.append(new_c) # Category is orphan: keep only parent
            
            else:
                new_categories.append(c) # Category is not orphan
        
        else:
            new_categories.append(c)
    
    return new_categories
