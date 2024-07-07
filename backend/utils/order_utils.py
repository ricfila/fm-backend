from backend.database.models import (
    Order,
    OrderMenuField,
    OrderProduct,
    OrderProductIngredient,
    Product,
)
from backend.models.orders import CreateOrderProductItem


async def check_products(
    products: list[CreateOrderProductItem], role_id: int
) -> tuple[bool, str, dict]:
    for product in products:
        product_db = await Product.get_or_none(
            id=product.product_id
        ).prefetch_related("dates", "ingredients", "roles", "variants")

        if not product_db:
            return (
                True,
                "PRODUCT_NOT_EXIST",
                {"product_id": product.product_id},
            )

        if not any(role.role_id == role_id for role in product_db.roles):
            return (
                True,
                "PRODUCT_ROLE_NOT_EXIST",
                {"product_id": product.product_id},
            )

        if not any(
            [await date.is_valid_product_date() for date in product_db.dates]
        ):
            return (
                True,
                "PRODUCT_DATE_NOT_VALID",
                {"product_id": product.product_id},
            )

        if list(product_db.variants) and not product.variant_id:
            return (
                True,
                "INPUT_PRODUCT_VARIANT",
                {
                    "product_id": product.product_id,
                    "variant_id": product.variant_id,
                },
            )

        if not any(
            variant.id == product.variant_id for variant in product_db.variants
        ):
            return (
                True,
                "PRODUCT_VARIANT_NOT_EXIST",
                {
                    "product_id": product.product_id,
                    "variant_id": product.variant_id,
                },
            )

        for ingredient in product.ingredients:
            if ingredient not in [
                ingredient.id for ingredient in product_db.ingredients
            ]:
                return (
                    True,
                    "PRODUCT_INGREDIENT_NOT_EXIST",
                    {
                        "product_id": product.product_id,
                        "ingredient_id": ingredient,
                    },
                )

        product._price = product_db.price

    return False, "", {}


async def create_order_products(
    products: list[CreateOrderProductItem],
    order: Order,
    order_menu_field: OrderMenuField | None = None,
) -> bool:
    for product in products:
        order_product = await OrderProduct.create(
            product_id=product.product_id,
            price=product._price,
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
