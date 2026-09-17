from fastapi import APIRouter, Depends
from tortoise.transactions import in_transaction

from backend.config import Session
from backend.database.models import Order, PaymentMethod
from backend.decorators import check_role
from backend.models.error import BadRequest, Conflict, NotFound, Unauthorized
from backend.models.orders import (
    CreateOrderItem,
    CreateOrderResponse,
    Order as OrderModel,
)
from backend.utils import ErrorCodes, Permission, TokenJwt, validate_token
from backend.utils.order_utils import (
    check_menus,
    check_products,
    create_order_menus,
    create_order_products,
    create_tickets,
    get_order_price,
    is_table_allowed_for_role,
)

create_order_router = APIRouter()


@create_order_router.post("/", response_model=CreateOrderResponse)
@check_role(Permission.CAN_ORDER)
async def create_order(
    item: CreateOrderItem,
    token: TokenJwt = Depends(validate_token),
):
    """
    Create a new order.

     **Permission**: can_order
    """

    if not item.products and not item.menus:
        raise BadRequest(code=ErrorCodes.NO_PRODUCTS_AND_MENUS, message="Nessun prodotto e nessun menù selezionato")

    eat_in = not item.is_take_away and item.has_tickets and not item.parent_order_id

    if eat_in:
        if not item.table:
            if not Session.settings.order_requires_confirmation:
                raise BadRequest(code=ErrorCodes.SET_TABLE, message="Specificare il numero del tavolo")
            
            if not item.guests:
                raise BadRequest(code=ErrorCodes.SET_GUESTS_NUMBER, message="Specificare il numero di coperti")
    
    else:
        if item.guests:
            raise BadRequest(code=ErrorCodes.METHOD_NOT_ALLOWED, message="Per quest'ordine non è consentito specificare il numero di coperti")
        
        if item.table:
            raise BadRequest(code=ErrorCodes.METHOD_NOT_ALLOWED, message="Per quest'ordine non è consentito specificare il tavolo")
    
        if item.is_take_away and item.parent_order_id:
            raise BadRequest(code=ErrorCodes.METHOD_NOT_ALLOWED, message="Un ordine figlio non può essere da asporto")
            
        if item.is_take_away and not item.has_tickets:
            raise BadRequest(code=ErrorCodes.METHOD_NOT_ALLOWED, message="Un ordine per asporto deve avere delle comande")


    async with in_transaction() as connection:
        await connection.execute_query(
            "SET TRANSACTION ISOLATION LEVEL SERIALIZABLE;"
        )

        if item.parent_order_id:
            parent_order = await Order.get_or_none(
                id=item.parent_order_id, using_db=connection
            )

            if not parent_order:
                raise NotFound(code=ErrorCodes.ORDER_NOT_FOUND)

        payment_method = await PaymentMethod.get_or_none(
            id=item.payment_method_id, is_deleted=False, using_db=connection
        )

        if not payment_method:
            raise NotFound(code=ErrorCodes.PAYMENT_METHOD_NOT_FOUND)
    
        if (
            item.table is not None
            and not await is_table_allowed_for_role(
                token.role_id, item.table, connection
            )
        ):
            raise Unauthorized(code=ErrorCodes.TABLE_NOT_ALLOWED_FOR_ROLE)

        has_error_products, error_code_products = await check_products(
            item.products, token.role_id, connection
        )

        if has_error_products:
            raise Conflict(code=error_code_products)

        has_error_menus, error_code_menus = await check_menus(
            item.menus, token.role_id, connection
        )

        if has_error_menus:
            raise Conflict(code=error_code_menus)

        guests = item.guests if eat_in else None
        order_price = await get_order_price(item, guests or 0)

        order = await Order.create(
            customer=item.customer,
            guests=guests,
            is_take_away=item.is_take_away,
            table=item.table if eat_in else None,
            needs_confirmation=bool(eat_in and not item.table),
            is_voucher=item.is_voucher,
            is_for_service=item.is_for_service,
            has_tickets=item.has_tickets,
            notes=item.notes,
            price=order_price,
            parent_order_id=item.parent_order_id,
            payment_method_id=item.payment_method_id,
            user_id=token.user_id,
            using_db=connection,
        )

        await create_order_products(item.products, order, connection)
        await create_order_menus(item.menus, order, connection)
        await create_tickets(order, connection)

    return CreateOrderResponse(order=OrderModel(**await order.to_dict()))
