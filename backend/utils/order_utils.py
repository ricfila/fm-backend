from tortoise.query_utils import Prefetch

from backend.database.models import (
    Menu,
    MenuField,
    MenuFieldProduct,
    Order,
    OrderMenu,
    OrderMenuField,
    OrderProduct,
    OrderProductIngredient,
    Product,
    ProductIngredient,
    ProductVariant,
)
from backend.models.orders import CreateOrderMenuItem, CreateOrderProductItem
from backend.utils import ErrorCodes


async def check_generic_product(
    product: CreateOrderProductItem, product_db: Product, is_menu: bool = False
) -> tuple[bool, ErrorCodes | None, dict | None]:
    product_price = product_db.price

    if is_menu:
        product_price = 0

    if list(product_db.variants) and not product.variant_id:
        return (
            True,
            ErrorCodes.INPUT_MENU_FIELD_PRODUCT_VARIANT
            if is_menu
            else ErrorCodes.INPUT_PRODUCT_VARIANT,
            {
                "product_id": product.product_id,
                "variant_id": product.variant_id,
            },
        )

    if product.variant_id:
        product_variant = await ProductVariant.get_or_none(
            id=product.variant_id, product=product_db
        )

        if not product_variant:
            return (
                True,
                ErrorCodes.MENU_FIELD_PRODUCT_VARIANT_NOT_EXIST
                if is_menu
                else ErrorCodes.PRODUCT_VARIANT_NOT_EXIST,
                {
                    "product_id": product.product_id,
                    "variant_id": product.variant_id,
                },
            )

        product_price += product_variant.price

    for ingredient in product.ingredients:
        product_ingredient = await ProductIngredient.get_or_none(
            id=ingredient, product=product_db
        )

        if not product_ingredient:
            return (
                True,
                ErrorCodes.MENU_FIELD_PRODUCT_INGREDIENT_NOT_EXIST
                if is_menu
                else ErrorCodes.PRODUCT_INGREDIENT_NOT_EXIST,
                {
                    "product_id": product.product_id,
                    "ingredient_id": ingredient,
                },
            )

        product_price += product_ingredient.price

    product._price = product_price

    return False, None, None


async def check_products(
    products: list[CreateOrderProductItem], role_id: int
) -> tuple[bool, ErrorCodes | None, dict | None]:
    for product in products:
        product_db = await Product.get_or_none(
            id=product.product_id
        ).prefetch_related("dates", "roles", "variants")

        if not product_db:
            return (
                True,
                ErrorCodes.PRODUCT_NOT_EXIST,
                {"product_id": product.product_id},
            )

        if not product.quantity:
            return (
                True,
                ErrorCodes.MISSING_PRODUCT_QUANTITY,
                {"product_id": product.product_id},
            )

        if not any(role.role_id == role_id for role in product_db.roles):
            return (
                True,
                ErrorCodes.PRODUCT_ROLE_NOT_EXIST,
                {"product_id": product.product_id},
            )

        if not any(
            [await date.is_valid_product_date() for date in product_db.dates]
        ):
            return (
                True,
                ErrorCodes.PRODUCT_DATE_NOT_VALID,
                {"product_id": product.product_id},
            )

        variant_ingredients_check = await check_generic_product(
            product, product_db
        )

        if variant_ingredients_check[0]:
            return variant_ingredients_check

    return False, None, None


async def create_order_products(
    products: list[CreateOrderProductItem],
    order: Order,
    order_menu_field: OrderMenuField | None = None,
) -> bool:
    for product in products:
        order_product = await OrderProduct.create(
            product_id=product.product_id,
            price=product._price * product.quantity,
            quantity=product.quantity,
            variant_id=product.variant_id,
            order=order,
            order_menu_field=order_menu_field,
        )

        for ingredient in set(product.ingredients):
            await OrderProductIngredient.create(
                order_product=order_product, product_ingredient_id=ingredient
            )

    return True


async def check_menu_products(
    products: list[CreateOrderProductItem],
    menu_field: MenuField,
    quantity: int,
) -> tuple[bool, ErrorCodes | None, dict | None]:
    for product in products:
        menu_field_product = await MenuFieldProduct.get_or_none(
            product_id=product.product_id, menu_field=menu_field
        ).prefetch_related(
            Prefetch(
                "product", queryset=Product.all().prefetch_related("variants")
            )
        )

        if not menu_field_product:
            return (
                True,
                ErrorCodes.MENU_FIELD_PRODUCT_NOT_EXIST,
                {
                    "menu_id": menu_field.menu_id,
                    "menu_field_id": menu_field.id,
                    "product_id": product.product_id,
                },
            )

        variant_ingredients_check = await check_generic_product(
            product, menu_field_product.product, True
        )

        if variant_ingredients_check[0]:
            error_details_updated = {
                "menu_id": menu_field.menu_id,
                "menu_field_id": menu_field.id,
            }
            error_details_updated.update(variant_ingredients_check[2])

            return (
                True,
                variant_ingredients_check[1],
                error_details_updated,
            )

        product.quantity = quantity
        product._price += menu_field_product.price

    return False, None, None


async def check_menus(
    menus: list[CreateOrderMenuItem], role_id: int
) -> tuple[bool, ErrorCodes | None, dict | None]:
    for menu in menus:
        menu_db = await Menu.get_or_none(id=menu.menu_id).prefetch_related(
            "dates", "menu_fields", "roles"
        )

        if not menu_db:
            return True, ErrorCodes.MENU_NOT_EXIST, {"menu_id": menu.menu_id}

        menu_price = menu_db.price

        if not any(role.role_id == role_id for role in menu_db.roles):
            return (
                True,
                ErrorCodes.MENU_ROLE_NOT_EXIST,
                {"menu_id": menu.menu_id},
            )

        if not any(
            [await date.is_valid_menu_date() for date in menu_db.dates]
        ):
            return (
                True,
                ErrorCodes.MENU_DATE_NOT_VALID,
                {"menu_id": menu.menu_id},
            )

        menu_fields_obligatory = {
            field.id for field in menu_db.menu_fields if not field.is_optional
        }
        menu_field_ids = {field.menu_field_id for field in menu.fields}

        if not menu_fields_obligatory.issubset(menu_field_ids):
            return (
                True,
                ErrorCodes.MISSING_OBLIGATORY_MENU_FIELDS,
                {"menu_id": menu.menu_id},
            )

        for field in menu.fields:
            menu_field = await MenuField.get_or_none(
                id=field.menu_field_id
            ).prefetch_related("field_products")

            if not menu_field:
                return (
                    True,
                    ErrorCodes.MENU_FIELD_NOT_EXIST,
                    {
                        "menu_id": menu.menu_id,
                        "menu_field_id": field.menu_field_id,
                    },
                )

            if len(field.products) < 1:
                return (
                    True,
                    ErrorCodes.MISSING_MENU_FIELD_PRODUCTS,
                    {
                        "menu_id": menu.menu_id,
                        "menu_field_id": field.menu_field_id,
                    },
                )

            if len(field.products) > menu_field.max_sortable_elements:
                return (
                    True,
                    ErrorCodes.MENU_FIELD_TOO_MANY_PRODUCTS,
                    {
                        "menu_id": menu.menu_id,
                        "menu_field_id": field.menu_field_id,
                    },
                )

            check_menu_field_products = await check_menu_products(
                field.products, menu_field, menu.quantity
            )

            if check_menu_field_products[0]:
                return check_menu_field_products

            for product in field.products:
                menu_price += product._price

        menu._price = menu_price

    return False, None, None


async def create_order_menus(
    menus: list[CreateOrderMenuItem], order: Order
) -> bool:
    for menu in menus:
        order_menu = await OrderMenu.create(
            menu_id=menu.menu_id,
            price=menu._price * menu.quantity,
            quantity=menu.quantity,
            order=order,
        )

        for field in menu.fields:
            order_menu_field = await OrderMenuField.create(
                order_menu=order_menu, menu_field_id=field.menu_field_id
            )

            await create_order_products(
                field.products, order, order_menu_field
            )

    return True
