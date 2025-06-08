from __future__ import annotations

import typing
import textwrap

import pytz
from tortoise.models import ReverseRelation

from backend.config import Session
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
        order_products: list[OrderProduct],
        include_price: bool = False,
        is_menu: bool = False,
        only_food: bool = False,
        only_drinks: bool = False,
    ) -> list[str] | list[tuple[str, float]]:
        products = []

        for order_product in order_products:
            if order_product.order_menu_field_id and not is_menu:
                continue

            product = await order_product.product

            if only_food and product.category != Category.FOOD:
                continue

            if only_drinks and product.category != Category.DRINK:
                continue

            product_quantity = order_product.quantity
            product_name = product.short_name

            product_variant = ""
            if (variant := order_product.variant) is not None:
                if (v := await variant) is not None:
                    product_variant = v.name

            product_ingredients = " ".join(
                [
                    f"+{order_product_ingredient.product_ingredient.name}"
                    for order_product_ingredient in order_product.order_product_ingredients
                ]
            )

            product_text = f"x{product_quantity} {product_name}"
            product_text += f" - {product_variant}" if product_variant else ""
            product_text += "\n"
            product_text += product_ingredients

            if not is_menu and include_price:
                if product_ingredients:
                    product_text += "\n"
                product_unit_cost = order_product.price / product_quantity
                product_text += f"{product_quantity} x {product_unit_cost:.2f}"

            if include_price:
                products.append((product_text, order_product.price))
            else:
                products.append(product_text)

        return products

    @classmethod
    async def _get_products_text(
        cls,
        order_products: list[OrderProduct],
        include_price: bool = False,
        max_width: int = MAX_WIDTH,
        only_food: bool = False,
        only_drinks: bool = False,
    ) -> str:
        result = ""
        products_data = await cls._get_products_data(
            order_products, include_price, False, only_food, only_drinks
        )

        for i, x in enumerate(products_data):
            product_text = x[0] if include_price else x
            product_price = x[1] if include_price else None

            price_text = f"€ {product_price:.2f}" if include_price else None
            width = (
                (max_width - len(price_text) - 1)
                if include_price
                else max_width
            )

            texts = []
            for j, y in enumerate(product_text.splitlines()):
                text = textwrap.wrap(
                    y,
                    width=width,
                    initial_indent=" " * 4 if j > 0 else "",
                    subsequent_indent=" " * 4,
                    break_long_words=False,
                )
                texts.extend(text)

            if include_price:
                result += cls._align_texts(texts[0], price_text)
            else:
                result += texts[0]

            result += "\n" if len(texts) > 1 else ""
            result += "\n".join(texts[1:])
            result += "\n" if i < len(products_data) - 1 else ""

        return result

    @classmethod
    async def _get_menu_data(
        cls,
        order_menu: ReverseRelation[OrderMenu],
        include_price: bool = False,
    ) -> list[
        tuple[str, list[ReverseRelation[OrderProduct]], float, int]
    ] | list[
        tuple[str, list[ReverseRelation[OrderProduct]], float, int, float]
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
            menu_unit_cost = order_menu.price / menu_quantity

            if include_price:
                menus.append(
                    (
                        menu_text,
                        menu_data,
                        menu_unit_cost,
                        menu_quantity,
                        order_menu.price,
                    )
                )
            else:
                menus.append(
                    (menu_text, menu_data, menu_unit_cost, menu_quantity)
                )

        return menus

    @classmethod
    async def _get_menu_products_text(
        cls,
        order_products: ReverseRelation[OrderProduct] | list[OrderProduct],
        max_width: int = MAX_WIDTH,
        only_food: bool = False,
        only_drinks: bool = False,
    ):
        products_data = await cls._get_products_data(
            order_products, False, True, only_food, only_drinks
        )

        texts = []
        for x in products_data:
            for i, y in enumerate(x.splitlines()):
                text = textwrap.wrap(
                    y,
                    max_width,
                    initial_indent=" " * 8 if i > 0 else " " * 4,
                    subsequent_indent=" " * 8,
                    break_long_words=False,
                )
                texts.extend(text)

        return "\n".join(texts)

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
            menu_unit_cost = x[2]
            menu_quantity = x[3]
            menu_price = x[4] if include_price else None

            price_text = f"€ {menu_price:.2f}" if include_price else None
            max_width = (
                (cls.MAX_WIDTH - len(price_text) - 1)
                if include_price
                else cls.MAX_WIDTH
            )
            menu_products_text = [
                await cls._get_menu_products_text(
                    p,
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

            if include_price:
                result += (
                    "\n" + " " * 4 + f"{menu_quantity} x {menu_unit_cost:.2f}"
                )
            result += "\n" if i < len(menu_data) - 1 else ""

        return result

    async def _get_ordered_products(self) -> list[OrderProduct]:
        enriched_products = []

        for op in self.order.order_products:
            product = await op.product
            subcategory = await product.subcategory if product else None

            subcategory_order = subcategory.order if subcategory else 0
            product_order = product.order if product else 0

            enriched_products.append(
                ((subcategory_order, product_order, op.id), op)
            )

        return [op for _, op in sorted(enriched_products)]

    async def _get_header(self) -> str:
        result = ""

        for x in Session.settings.receipt_header.split("\n"):
            result += x.center(self.MAX_WIDTH) + "\n"

        if Session.settings.receipt_header:
            result += "\n"

        result += f"* Scontrino n. {self.order.id}\n"
        result += "* Operatore di cassa:\n"
        result += " " * 4 + self.order.user.username + "\n"
        result += (
            "* "
            + self.order.created_at.astimezone(
                pytz.timezone("Europe/Rome")
            ).strftime("%d/%m/%Y %H:%M:%S")
            + "\n"
        )
        customer = (
            self.order.customer
            if not self.order.parent_order
            else self.order.parent_order.customer
        )
        result += "* CLIENTE: " + customer.upper() + "\n"

        if self.order.is_take_away:
            result += "* Per asporto: si" + "\n"
        else:
            if self.order.table:
                result += "* Tavolo: " + str(self.order.table) + "\n"
            elif self.order.parent_order:
                result += (
                    "* Tavolo: " + str(self.order.parent_order.table) + "\n"
                )
            if self.order.is_confirm:
                result += (
                    "* Data conferma: "
                    + self.order.confirmed_at.astimezone(
                        pytz.timezone("Europe/Rome")
                    ).strftime("%d/%m/%Y %H:%M:%S")
                    + "\n"
                )

        if self.order.parent_order:
            result += "* Aggiunta a: " + str(self.order.parent_order_id) + "\n"

        if self.order.is_voucher:
            result += "* Buono: si" + "\n"

        result += "\n"

        return result

    async def _render_receipt_text(self) -> str:
        receipt_text = await self._get_header()

        if not self.order.is_take_away and not self.order.parent_order:
            text_left = f"x{self.order.guests} Coperti"
            text_right = Session.settings.cover_charge * self.order.guests
            receipt_text += self._align_texts(text_left, f"€ {text_right:.2f}")
            receipt_text += "\n"
            receipt_text += (
                " " * 4
                + f"{self.order.guests} x {Session.settings.cover_charge}"
            )
            receipt_text += "\n"

        products_text = await self._get_products_text(
            await self._get_ordered_products(), True
        )
        receipt_text += products_text

        if products_text:
            receipt_text += "\n"

        menu_text = await self._get_menu_text(self.order.order_menus, True)
        receipt_text += menu_text

        if menu_text:
            receipt_text += "\n"

        total_price = (
            f"€ {self.order.price:.2f}"
            if not self.order.is_voucher
            else "€ 0.00"
        )
        receipt_text += self._align_texts("TOTALE:", total_price)

        return receipt_text

    async def _render_kitchen_text(
        self, only_food: bool = False, only_drinks: bool = False
    ) -> str:
        kitchen_text = await self._get_header()

        if not self.order.is_take_away and not self.order.parent_order:
            kitchen_text += f"x{self.order.guests} Coperti"
            kitchen_text += "\n"

        products_text = await self._get_products_text(
            await self._get_ordered_products(),
            only_food=only_food,
            only_drinks=only_drinks,
        )
        kitchen_text += products_text

        if products_text:
            kitchen_text += "\n"

        menu_text = await self._get_menu_text(
            self.order.order_menus,
            only_food=only_food,
            only_drinks=only_drinks,
        )
        kitchen_text += menu_text

        return kitchen_text

    async def generate_text_for_printer(self, printer_type: PrinterType):
        printer_formatters = {
            PrinterType.RECEIPT: self._render_receipt_text,
            PrinterType.DRINKS: lambda: self._render_kitchen_text(
                only_drinks=True
            ),
            PrinterType.FOOD: lambda: self._render_kitchen_text(
                only_food=True
            ),
            PrinterType.FOOD_AND_DRINKS: self._render_kitchen_text,
        }

        return await printer_formatters[printer_type]()
