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


async def collapseCategories(categories, parent_field, changes, connection):
    new_categories = []

    for c in categories:
        parent_id = getattr(c, parent_field)

        if parent_id is not None:
            if not any(k.id == parent_id for k in categories + new_categories):
                new_c = await Category.get_or_none(id=parent_id, using_db=connection)
                if not new_c:
                    raise NotFound(ErrorCodes.CATEGORY_NOT_FOUND)
                new_categories.append(new_c)
            
            changes[c.id] = parent_id
        
        else:
            new_categories.append(c)
    
    return new_categories, collapseChangesChains(changes)


async def collapseOrphanCategories(categories, changes, connection):
    new_categories = []

    for c in categories:
        parent_id = c.parent_category_id

        if parent_id is not None:
            if not any(k.id == parent_id for k in categories + new_categories):
                new_c = await Category.get_or_none(id=parent_id, using_db=connection)
                if not new_c:
                    raise NotFound(ErrorCodes.CATEGORY_NOT_FOUND)
                new_categories.append(new_c) # Category is orphan: keep only parent
                changes[c.id] = parent_id
            
            else:
                new_categories.append(c) # Category is not orphan
        
        else:
            new_categories.append(c)
    
    return new_categories, collapseChangesChains(changes)


def collapseChangesChains(changes):
    resolved_changes = {}

    for from_id in changes:
        current_to = changes[from_id]
        
        while current_to in changes:
            current_to = changes[current_to]
        
        resolved_changes[from_id] = current_to

    return {k: v for k, v in resolved_changes.items() if k != v}
