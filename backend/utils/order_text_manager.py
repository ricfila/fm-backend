from __future__ import annotations

import typing
import textwrap

import pytz
from tortoise.models import ReverseRelation

from backend.utils import PrinterType, Category

if typing.TYPE_CHECKING:
    from backend.database.models import Order, OrderProduct, OrderMenu


class OrderTextManager:
    MAX_WIDTH = 42

    def __init__(self, order: Order):
        self.order = order

    @staticmethod
    def _align_texts(left: str, right: str) -> str:
        width = OrderTextManager.MAX_WIDTH
        space = width - len(left) - len(right)

        if space < 0:
            left = left[: width // 2 - 1]
            right = right[: width // 2 - 1]
            space = 1

        return left + " " * space + right

    @staticmethod
    async def _get_products_data(
        order_products: ReverseRelation[OrderProduct],
        include_price: bool = False,
        is_menu: bool = False,
        only_food: bool = False,
        only_drinks: bool = False,
    ) -> list[str] | list[tuple[str, float]]:
        products = []

        for order_product in order_products:
            if order_product.order_menu_field_id and not is_menu:
                continue

            if (
                only_food
                and (await order_product.product).category != Category.FOOD
            ):
                continue

            if (
                only_drinks
                and (await order_product.product).category != Category.DRINK
            ):
                continue

            product_quantity = order_product.quantity
            product_name = (await order_product.product).short_name
            product_variant = ""
            if (variant := await order_product.variant) is not None:
                product_variant = variant.name
            product_ingredients = ", ".join(
                [
                    f"x{order_product_ingredient.quantity} {order_product_ingredient.product_ingredient.name}"
                    for order_product_ingredient in order_product.order_product_ingredients
                ]
            )

            product_text = f"x{product_quantity} {product_name}"
            product_text += f" - {product_variant}" if product_variant else ""
            product_text += (
                f" ({product_ingredients})" if product_ingredients else ""
            )

            if include_price:
                products.append((product_text, order_product.price))
            else:
                products.append(product_text)

        return products

    @classmethod
    async def _get_products_text(
        cls,
        order_products: ReverseRelation[OrderProduct],
        include_price: bool = False,
        is_menu: bool = False,
        max_width: int = MAX_WIDTH,
        only_food: bool = False,
        only_drinks: bool = False,
    ) -> str:
        result = ""
        products_data = await cls._get_products_data(
            order_products, include_price, is_menu, only_food, only_drinks
        )

        for i, x in enumerate(products_data):
            product_text = x[0] if include_price else x
            product_price = x[1] if include_price else None

            price_text = f"€ {product_price:.2f}" if include_price else None
            texts = textwrap.wrap(
                product_text,
                (max_width - len(price_text) - 1)
                if include_price
                else max_width,
                initial_indent=" " * (4 if is_menu else 0),
                subsequent_indent=" " * (8 if is_menu else 4),
                break_long_words=False,
            )

            if include_price:
                result += cls._align_texts(texts[0], price_text)
            else:
                result += texts[0]

            result += "\n" if len(texts) > 1 else ""
            result += " ".join(texts[1:]) if is_menu else "\n".join(texts[1:])
            result += (
                ("; " if is_menu else "\n")
                if i < len(products_data) - 1
                else ""
            )

        return result

    @classmethod
    async def _get_menu_data(
        cls,
        order_menu: ReverseRelation[OrderMenu],
        include_price: bool = False,
    ) -> list[tuple[str, list[ReverseRelation[OrderProduct]]]] | list[
        tuple[str, list[ReverseRelation[OrderProduct]], float]
    ]:
        menus = []

        for order_menu in order_menu:
            menu_quantity = order_menu.quantity
            order_name = (await order_menu.menu).short_name

            menu_text = f"x{menu_quantity} {order_name}"
            menu_data = [
                x.order_menu_field_products
                for x in order_menu.order_menu_fields
            ]

            if include_price:
                menus.append((menu_text, menu_data, order_menu.price))
            else:
                menus.append((menu_text, menu_data))

        return menus

    @classmethod
    async def _get_menu_text(
        cls,
        order_menu: ReverseRelation[OrderMenu],
        include_price: bool = False,
        only_food: bool = False,
        only_drinks: bool = False,
    ) -> str:
        result = ""
        menu_data = await cls._get_menu_data(order_menu, include_price)

        for i, x in enumerate(menu_data):
            menu_text = x[0]
            menu_products = x[1]
            menu_price = x[2] if include_price else None

            price_text = f"€ {menu_price:.2f}" if include_price else None
            max_width = (
                (cls.MAX_WIDTH - len(price_text) - 1)
                if include_price
                else cls.MAX_WIDTH
            )
            menu_products_text = [
                await cls._get_products_text(
                    p,
                    is_menu=True,
                    max_width=max_width,
                    only_food=only_food,
                    only_drinks=only_drinks,
                )
                for p in menu_products
            ]

            if all(map(lambda pt: not pt, menu_products_text)):
                continue

            if not menu_products_text:
                continue

            if include_price:
                result += cls._align_texts(menu_text, price_text) + "\n"
            else:
                result += menu_text + "\n"

            result += "\n".join(menu_products_text)
            result += "\n" if i < len(menu_data) - 1 else ""

        return result

    async def _get_header(self) -> str:
        result = ""

        receipt_number = f"Scontrino n. {self.order.id}"
        receipt_date = self.order.created_at.astimezone(
            pytz.timezone("Europe/Rome")
        ).strftime("%d/%m/%Y %H:%M")
        result += self._align_texts(receipt_number, receipt_date)
        result += "\n"

        if self.order.is_take_away:
            result += "Per asporto? si"
        else:
            result += self._align_texts(
                f"Tavolo n. {self.order.table}",
                f"Coperti n. {self.order.guests}",
            )

        result += "\n\n"

        return result

    async def _get_price(self) -> float:
        result = 0

        result += sum(
            x.price
            for x in self.order.order_products
            if x.order_menu_field_id is None
        )
        result += sum(x.price for x in self.order.order_menus)

        return result

    async def _render_receipt_text(self) -> str:
        receipt_text = await self._get_header()

        products_text = await self._get_products_text(
            self.order.order_products, True
        )
        receipt_text += products_text

        if products_text:
            receipt_text += "\n"

        menu_text = await self._get_menu_text(self.order.order_menus, True)
        receipt_text += menu_text

        if menu_text:
            receipt_text += "\n"

        receipt_text += self._align_texts(
            "TOTALE:", f"€ {(await self._get_price()):.2f}"
        )

        return receipt_text

    async def _render_drinks_text(self) -> str:
        drinks_text = await self._get_header()

        products_text = await self._get_products_text(
            self.order.order_products, only_drinks=True
        )
        drinks_text += products_text

        if products_text:
            drinks_text += "\n"

        menu_text = await self._get_menu_text(
            self.order.order_menus, only_drinks=True
        )
        drinks_text += menu_text

        return drinks_text

    async def _render_food_text(self) -> str:
        food_text = await self._get_header()

        products_text = await self._get_products_text(
            self.order.order_products, only_food=True
        )
        food_text += products_text

        if products_text:
            food_text += "\n"

        menu_text = await self._get_menu_text(
            self.order.order_menus, only_food=True
        )
        food_text += menu_text

        return food_text

    async def _render_food_and_drinks_text(self) -> str:
        food_and_drinks_text = await self._get_header()

        products_text = await self._get_products_text(
            self.order.order_products
        )
        food_and_drinks_text += products_text

        if products_text:
            food_and_drinks_text += "\n"

        menu_text = await self._get_menu_text(self.order.order_menus)
        food_and_drinks_text += menu_text

        return food_and_drinks_text

    async def generate_text_for_printer(self, printer_type: PrinterType):
        printer_formatters = {
            PrinterType.RECEIPT: self._render_receipt_text,
            PrinterType.DRINKS: self._render_drinks_text,
            PrinterType.FOOD: self._render_food_text,
            PrinterType.FOOD_AND_DRINKS: self._render_food_and_drinks_text,
        }

        return await printer_formatters[printer_type]()
