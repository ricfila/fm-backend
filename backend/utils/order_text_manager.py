from __future__ import annotations

import re
import typing
import textwrap

import pytz
from tortoise.models import ReverseRelation

from backend.config import Session
from backend.utils import PrinterType

if typing.TYPE_CHECKING:
    from backend.database.models import Category, Order, OrderProduct, OrderMenu


class OrderTextManager:
    MAX_WIDTH = 48

    def __init__(self, order: Order, category: Category):
        self.order = order
        self.category = category

    @staticmethod
    def _visual_length(text: str) -> int:
        length = 0
        pattern = re.compile(r"<DOUBLE>(.*?)</DOUBLE>")

        pos = 0
        for match in pattern.finditer(text):
            start, end = match.span()
            before = text[pos:start]
            length += len(before)
            length += len(match.group(1)) * 2
            pos = end

        length += len(text[pos:])
        return length

    @staticmethod
    def _align_texts(left: str, right: str) -> str:
        width = OrderTextManager.MAX_WIDTH

        left_len = OrderTextManager._visual_length(left)
        right_len = OrderTextManager._visual_length(right)

        space = max(width - left_len - right_len, 1)

        return left + " " * space + right

    @staticmethod
    def shorten_by_chars(text: str, width: int, placeholder="..") -> str:
        if len(text) <= width:
            return text
        cut_len = width - len(placeholder)
        if cut_len <= 0:
            return placeholder[:width]
        return text[:cut_len] + placeholder
    
    @staticmethod
    def _row_in_square(text: str = None, is_first: bool = False, is_last: bool = False) -> str:
        width = OrderTextManager.MAX_WIDTH

        if is_first:
            return "╔" + "═"*(width - 2) + "╗\n"
        if is_last:
            return "╚" + "═"*(width - 2) + "╝\n"
        if text is not None:
            return "║" + text + " "*(width - len(text) - 2) + "║\n"
        return ""

    @staticmethod
    def _get_products_data(
        order_products: list[OrderProduct],
        include_price: bool = False,
        is_menu: bool = False
    ) -> list[dict]:
        products = []

        for order_product in order_products:
            if order_product.order_menu_field_id and not is_menu:
                continue

            product = order_product.product

            product_quantity = order_product.quantity
            product_name = product.short_name
            product_notes = order_product.notes

            product_variant = ""
            if (variant := order_product.variant) is not None:
                product_variant = variant.name

            product_ingredients = " ".join(
                [
                    f"+{order_product_ingredient.ingredient.name}"
                    for order_product_ingredient in order_product.order_product_ingredients
                ]
            )

            product_main_text = product_name
            if product_variant:
                product_main_text += f" - {product_variant}"

            product_data = {
                "quantity": str(product_quantity),
                "main_text": product_main_text,
                "ingredients": product_ingredients
            }

            if product_notes is not None:
                product_data["notes"] = product_notes

            if include_price:
                product_data["unit_price"] = (
                    order_product.price / product_quantity
                )
                product_data["total_price"] = order_product.price

            products.append(product_data)

        return products

    @classmethod
    def _get_products_text(
        cls,
        order_products: list[OrderProduct],
        include_price: bool = False,
        max_width: int = MAX_WIDTH,
        large_quantity: bool = True
    ) -> str:
        product_blocks = []

        products_data = cls._get_products_data(order_products, include_price, is_menu=False)

        for product in products_data:
            lines = []

            quantity = product["quantity"]
            main_text = product["main_text"]
            ingredients = product["ingredients"]
            notes = product.get("notes")
            unit_price = product.get("unit_price")
            total_price = product.get("total_price")

            price_text = f"EURO {total_price:.2f}" if include_price else ""
            width = (
                (max_width - len(price_text) - 1)
                if include_price
                else max_width
            )

            quantity_len = len(quantity) + 1
            if large_quantity: quantity_len *= 2

            width_without_quantity = width - quantity_len
            wrap_width = width_without_quantity // 2
            indent = " " * quantity_len

            wrapped_main = textwrap.wrap(
                main_text,
                width=wrap_width,
                break_long_words=False,
            )

            first_double = cls.shorten_by_chars(
                wrapped_main[0].strip(), wrap_width
            )
            if large_quantity:
                full_line = f"<DOUBLE>{quantity} {first_double}</DOUBLE>"
            else:
                full_line = f"{quantity} <DOUBLE>{first_double}</DOUBLE>"

            if include_price:
                full_line = cls._align_texts(full_line, price_text)
            lines.append(full_line)

            for line in wrapped_main[1:]:
                shortened = cls.shorten_by_chars(line, wrap_width)
                lines.append(f"{indent}<DOUBLE>{shortened}</DOUBLE>")

            if ingredients:
                ingredients_wrap_width = width_without_quantity
                ingredient_lines = textwrap.wrap(
                    ingredients,
                    width=ingredients_wrap_width,
                    break_long_words=False,
                )
                for line in ingredient_lines:
                    shortened = cls.shorten_by_chars(
                        line, ingredients_wrap_width
                    )
                    lines.append(f"{indent}{shortened}")

            if include_price and unit_price is not None:
                unit_line = f"{quantity[1:]} x {unit_price:.2f}"
                lines.append(f"{indent}{unit_line}")
            
            if notes is not None:
                lines.append(f"{indent}└ {notes}")

            product_blocks.append("\n".join(lines))

        return "\n".join(product_blocks)

    @classmethod
    def _get_menu_data(
        cls,
        order_menu: ReverseRelation[OrderMenu],
        include_price: bool = False,
    ) -> list[dict]:
        menus = []

        for order in order_menu:
            menu_quantity = order.quantity
            order_name = order.menu.short_name
            menu_unit_cost = order.price / menu_quantity
            menu_price = order.price if include_price else None

            menu_data = {
                "quantity": f"x{menu_quantity}",
                "name": order_name,
                "unit_price": menu_unit_cost,
                "price": menu_price,
                "products_per_field": [
                    x.order_menu_field_products
                    for x in order.order_menu_fields
                ],
            }

            menus.append(menu_data)

        return menus

    @classmethod
    def _get_menu_products_text(
        cls,
        order_products: ReverseRelation[OrderProduct],
        max_width: int = MAX_WIDTH
    ):
        blocks = []

        products_data = cls._get_products_data(
            list(order_products),
            include_price=False,
            is_menu=True
        )

        for product in products_data:
            lines = []

            quantity = product["quantity"]
            main_text = product["main_text"]
            ingredients = product["ingredients"]

            wrap_width = max_width - len(quantity) - 1

            wrapped_main = textwrap.wrap(
                main_text, width=wrap_width, break_long_words=False
            )

            first_line = cls.shorten_by_chars(
                wrapped_main[0].strip(), wrap_width
            )
            lines.append(f"{' ' * 4}{quantity} {first_line}")

            for line in wrapped_main[1:]:
                shortened = cls.shorten_by_chars(line, wrap_width)
                lines.append(f"{' ' * 8}{shortened}")

            if ingredients:
                ingredient_lines = textwrap.wrap(
                    ingredients, width=wrap_width, break_long_words=False
                )
                for line in ingredient_lines:
                    shortened = cls.shorten_by_chars(line, wrap_width)
                    lines.append(f"{' ' * 8}{shortened}")

            blocks.append("\n".join(lines))

        return "\n".join(blocks)

    @classmethod
    def _get_menu_text(
        cls,
        order_menu: ReverseRelation[OrderMenu],
        include_price: bool = False
    ) -> str:
        menu_blocks = []
        menu_data = cls._get_menu_data(order_menu, include_price)

        for menu in menu_data:
            lines = []

            quantity = menu["quantity"]
            name = menu["name"]
            unit_price = menu["unit_price"]
            total_price = menu["price"]
            products_per_field = menu["products_per_field"]

            price_text = f"€ {total_price:.2f}" if include_price else ""
            width = (
                (cls.MAX_WIDTH - len(price_text) - 1)
                if include_price
                else cls.MAX_WIDTH
            )
            wrap_width = width // 2
            indent = " " * 4

            wrapped_name = textwrap.wrap(
                name, width=wrap_width, break_long_words=False
            )

            first_line = f"{quantity} <DOUBLE>{cls.shorten_by_chars(wrapped_name[0], wrap_width)}</DOUBLE>"
            if include_price:
                first_line = cls._align_texts(first_line, price_text)

            lines.append(first_line)

            for line in wrapped_name[1:]:
                shortened = cls.shorten_by_chars(line, wrap_width)
                lines.append(f"{indent}<DOUBLE>{shortened}</DOUBLE>")

            for product_list in products_per_field:
                menu_products_text = cls._get_menu_products_text(
                    product_list,
                    max_width=width
                )

                if menu_products_text.strip():
                    lines.append(menu_products_text)

            if include_price:
                lines.append(f"{indent}{quantity[1:]} x {unit_price:.2f}")

            menu_blocks.append("\n".join(lines))

        return "\n".join(menu_blocks)

    def _get_ordered_products(self) -> list[OrderProduct]:
        enriched_products = []

        for op in self.order.order_products:
            if op.category_id != self.category.id:
                continue

            product = op.product
            subcategory = product.subcategory if product else None

            subcategory_order = subcategory.order if subcategory else 0
            product_order = product.order if product else 0

            enriched_products.append(
                ((subcategory_order, product_order, op.id), op)
            )

        return [op for _, op in sorted(enriched_products)]

    def _get_header(self) -> str:
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
                result += "* Tavolo: " + self.order.table + "\n"
            elif self.order.parent_order:
                result += (
                    "* Tavolo: " + self.order.parent_order.table + "\n"
                )
            if self.order.is_confirmed:
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
    
    
    def _get_short_header(self) -> str:
        result = ""

        category_name = self.category.name.upper()
        category_name = (f"« {category_name} »").center(self.MAX_WIDTH // 2)
        date_time = self.order.created_at.astimezone(
            pytz.timezone("Europe/Rome")
        ).strftime("%d/%m/%Y %H:%M")

        if self.category.id == 5:
            row1 = "« HOSTARIA »".center(self.MAX_WIDTH // 2)
            row2 = "CENTRO PARROCCHIALE".center(self.MAX_WIDTH // 2)
            result += f"<DOUBLE>{row1}</DOUBLE>\n<DOUBLE>{row2}</DOUBLE>\n"
        else:
            result += f"<DOUBLE>{category_name}</DOUBLE>\n"
        row = f"Ordine n. {self.order.id} - {self.order.user.username} {date_time}"
        result += row + " "*(self.MAX_WIDTH - len(row))

        result += self._row_in_square(is_first=True)
        
        customer = (
            self.order.customer
            if not self.order.parent_order
            else self.order.parent_order.customer
        )
        guests = (
            "   (" + str(self.order.guests) + " copert" + ("o" if self.order.guests == 1 else "i") + ")"
            if self.order.guests is not None
            else ""
        )
        result += self._row_in_square(" CLIENTE: " + customer.upper() + guests)

        if self.order.table:
            result += self._row_in_square(" TAVOLO:  " + self.order.table)
        elif self.order.parent_order:
            result += self._row_in_square(" TAVOLO:  " + self.order.parent_order.table)
        
        if self.order.is_confirmed and self.order.confirmed_by is not None:
            result += self._row_in_square(
                " Confermato da " +
                self.order.confirmed_by.username +
                " alle " + self.order.confirmed_at.astimezone(
                    pytz.timezone("Europe/Rome")
                ).strftime("%H:%M")
            )
        
        result += self._row_in_square(is_last=True)

        if self.order.notes is not None:
            result += "NOTE: " + self.order.notes + "\n"

        result += "\n"

        return result

    def _render_receipt_text(self) -> str:
        receipt_text = self._get_header()

        if (
            not self.order.is_take_away
            and not self.order.parent_order
            and self.order.guests
        ):
            text_left = f"x{self.order.guests} <DOUBLE>Coperti</DOUBLE>"
            text_right = Session.settings.cover_charge * self.order.guests
            receipt_text += self._align_texts(text_left, f"€ {text_right:.2f}")
            receipt_text += "\n"
            receipt_text += (
                " " * 4
                + f"{self.order.guests} x {Session.settings.cover_charge}"
            )
            receipt_text += "\n"

        products_text = self._get_products_text(self._get_ordered_products(), include_price=True)
        receipt_text += products_text

        if products_text:
            receipt_text += "\n"

        menu_text = self._get_menu_text(self.order.order_menus, True)
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

    def _render_ticket_text(self) -> str:
        ticket_text = self._get_short_header()

        #if self.order.guests:
        #    ticket_text += f"{self.order.guests} <DOUBLE>Coperti</DOUBLE>"
        #    ticket_text += "\n"

        products_text = self._get_products_text(self._get_ordered_products(), include_price=True)
        ticket_text += products_text

        if products_text:
            ticket_text += "\n"

        menu_text = self._get_menu_text(self.order.order_menus)
        ticket_text += menu_text

        if menu_text:
            ticket_text += "\n"

        return ticket_text

    def generate_text_for_printer(self, printer_type: PrinterType):
        if printer_type == PrinterType.RECEIPT:
            return self._render_receipt_text()
        elif printer_type == PrinterType.TICKET:
            return self._render_ticket_text()
        
        return None
