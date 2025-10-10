import datetime
import pytz

from fastapi import APIRouter, Depends
from tortoise.transactions import in_transaction
from tortoise.exceptions import IntegrityError

from backend.config import Session
from backend.database.models import Order, OrderProduct, Product, Revision
from backend.decorators import check_role
from backend.models.error import Conflict, NotFound
from backend.models import BaseResponse
from backend.models.orders import (
    CreateOrderItem
)
from backend.utils import ErrorCodes, Permission, TokenJwt, validate_token

update_order_router = APIRouter()


@update_order_router.put("/{order_id}", response_model=BaseResponse)
@check_role(Permission.CAN_ORDER)
async def create_order(
    order_id: int,
    item: CreateOrderItem,
    token: TokenJwt = Depends(validate_token),
):
    """
    Update an order from id.

    **Permission**: can_order
    """

    async with in_transaction() as connection:
        await connection.execute_query(
            "SET TRANSACTION ISOLATION LEVEL SERIALIZABLE;"
        )

        order = await Order.get_or_none(
            id=order_id, using_db=connection
        )

        if not order:
            raise NotFound(code=ErrorCodes.ORDER_NOT_FOUND)
        
        old_price = float(order.price)
        new_price = old_price

        order.customer = item.customer
        order.guests = item.guests
        order.is_take_away = item.is_take_away
        order.table = item.table
        order.is_voucher = item.is_voucher
        order.has_tickets = item.has_tickets
        order.notes = item.notes
        order.payment_method_id = item.payment_method_id
        order.is_for_service = item.is_for_service

        edited_products = 0
        for product in item.products:
            if product.edited_product:
                edited_products += 1
                p = await Product.get_or_none(id=product.product_id)
                
                if product.original_quantity == 0:
                    try:
                        await OrderProduct.create( #Some fields has been omitted
                            product_id=product.product_id,
                            quantity=product.quantity,
                            price=product.quantity * p.price,
                            variant_id=product.variant_id,
                            notes=product.notes,
                            order=order,
                            category_id=product.category_id,
                            using_db=connection,
                        )
                        new_price += product.quantity * float(p.price)
                    except IntegrityError:
                        raise Conflict(ErrorCodes.ORDER_UPDATE_FAILED, message=f"Errore durante la creazione del prodotto order_product del prodotto con id {product.product_id}")
                else:
                    op = await OrderProduct.filter(order_id=order_id, product_id=product.product_id).using_db(connection).first()
                    if product.quantity == 0:
                        try:
                            await op.delete(using_db=connection)
                            new_price -= op.quantity * float(p.price)
                        except IntegrityError:
                            raise Conflict(ErrorCodes.ORDER_UPDATE_FAILED, message=f"Errore durante l'eliminazione del prodotto order_product {op.id}")
                    else:
                        delta_price = (product.quantity - product.original_quantity) * float(p.price)
                        op.quantity = product.quantity
                        op.notes = product.notes
                        op.price = float(op.price) + delta_price

                        try:
                            await op.save(using_db=connection)
                            new_price += float(delta_price)
                        except IntegrityError:
                            raise Conflict(ErrorCodes.ORDER_UPDATE_FAILED, message=f"Errore durante l'aggiornamento del prodotto order_product {op.id}")

        order.price = new_price

        try:
            await order.save(using_db=connection)

            await Revision.create(
                order=order,
                user_id=token.user_id,
                price_difference=(new_price-old_price),
                edited_products=edited_products
            )
        except IntegrityError:
            raise Conflict(ErrorCodes.ORDER_UPDATE_FAILED, message="Errore durante il salvataggio dell'ordine aggiornato")

    return BaseResponse()
