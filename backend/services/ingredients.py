import datetime
from tortoise.backends.base.client import TransactionContext

async def get_ingredient_stock(
        connection: TransactionContext,
        ingredient_id: int = None,
        ward: str = None,
        await_cooking_time: bool = False,
        only_monitored: bool = False,
        only_locked: bool = False
    ):
    query_stock = """
    SELECT
        i.id,
        i.name,
        i.ward,
        i.is_monitored,
        i.sell_if_stocked,
        i.cooking_time,
        i.target_quantity,
        s.added_stock,
        COALESCE(od.default_q, 0) + COALESCE(od.choosen_q, 0) AS consumed_stock,
        s.stock_starting_from
    FROM ingredient i
    LEFT JOIN (
        SELECT
            ingredient_id,
            SUM(quantity) AS added_stock,
            MIN(available_from) AS stock_starting_from
        FROM stock
        WHERE is_valid
        GROUP BY ingredient_id
    ) AS s ON s.ingredient_id = i.id
    LEFT JOIN LATERAL (
        SELECT
            SUM(
                CASE
                    WHEN pi.is_default AND NOT pi.is_deleted
                    THEN op.quantity * pi.max_quantity
                    ELSE 0
                END
            ) AS default_q,
            SUM(
                CASE
                    WHEN opi.order_product_id IS NOT NULL
                    THEN op.quantity * opi.quantity
                    ELSE 0
                END
            ) AS choosen_q
        FROM order_product op
        JOIN "order" o ON o.id = op.order_id
        LEFT JOIN product_ingredient pi ON pi.product_id = op.product_id AND pi.ingredient_id = i.id
        LEFT JOIN order_product_ingredient opi ON opi.order_product_id = op.id AND opi.ingredient_id = i.id
        WHERE
            (s.stock_starting_from IS NULL OR o.created_at > s.stock_starting_from)
    """ + ("""
            AND (i.cooking_time IS NULL OR NOT o.has_tickets OR (
                o.confirmed_at IS NOT NULL AND
                o.confirmed_at + (
                    (SELECT print_delay FROM category WHERE id = op.category_id) * INTERVAL '1 second'
                ) - (i.cooking_time * INTERVAL '1 second') < CURRENT_TIMESTAMP
            ))
           """ if await_cooking_time else "") + """
    ) AS od ON TRUE    
    WHERE"""

    if ingredient_id is None:
        query_stock += " NOT i.is_deleted"
        if only_locked:
            query_stock += " AND i.sell_if_stocked"
        else:
            if ward is not None:
                query_stock += f" AND i.ward = '{ward}'"
                if only_monitored:
                    query_stock += " AND i.is_monitored"
            else:
                if only_monitored:
                    query_stock += " AND i.is_monitored"
    else:
       query_stock += f" i.id = {ingredient_id}"
    
    query_stock += """
    ORDER BY i.id;
    """

    return await connection.execute_query_dict(query_stock)


async def get_ingredients_completed_quantities(
        connection: TransactionContext,
        ward: str = None,
        from_date: str = None,
        to_date: str = None,
        only_monitored: bool = False,
    ):
    query = f"""
SELECT
    i.id,
    i.name,
    i.ward,
    i.is_monitored,
    COALESCE(d.total_sold, 0) + COALESCE(ch.total_sold, 0) AS sold_quantity,
    COALESCE(d.total_completed, 0) + COALESCE(ch.total_completed, 0) AS completed_quantity
FROM ingredient i
LEFT JOIN (
    SELECT
        pi.ingredient_id,
        SUM(
            CASE
                WHEN tk.completed_at IS NULL AND NOT o.is_done
                THEN op.quantity * pi.max_quantity
                ELSE 0
            END
        ) AS total_sold,
        SUM(
            CASE
                WHEN tk.completed_at IS NOT NULL OR o.is_done
                THEN op.quantity * pi.max_quantity
                ELSE 0
            END
        ) AS total_completed
    FROM product_ingredient pi
    JOIN order_product op ON op.product_id = pi.product_id
    JOIN "order" o ON o.id = op.order_id
    LEFT JOIN ticket tk ON tk.order_id = op.order_id AND tk.category_id = op.category_id
    WHERE
        NOT pi.is_deleted
        AND pi.is_default
        AND NOT o.is_deleted
        AND o.created_at >= '{from_date}' AND o.created_at < '{to_date}'
    GROUP BY pi.ingredient_id
) AS d ON d.ingredient_id = i.id
LEFT JOIN (
    SELECT
        opi.ingredient_id,
        SUM(
            CASE
                WHEN tk.completed_at IS NULL AND NOT o.is_done
                THEN op.quantity * opi.quantity
                ELSE 0
            END
        ) AS total_sold,
        SUM(
            CASE
                WHEN tk.completed_at IS NOT NULL OR o.is_done
                THEN op.quantity * opi.quantity
                ELSE 0
            END
        ) AS total_completed
    FROM order_product_ingredient opi
    JOIN order_product op ON op.id = opi.order_product_id
    JOIN "order" o ON o.id = op.order_id
    LEFT JOIN ticket tk ON tk.order_id = op.order_id AND tk.category_id = op.category_id
    WHERE
        NOT o.is_deleted
        AND o.created_at >= '{from_date}' AND o.created_at < '{to_date}'
    GROUP BY opi.ingredient_id
) AS ch ON ch.ingredient_id = i.id
WHERE NOT i.is_deleted AND i.is_monitored AND i.ward = '{ward}'
ORDER BY i.id;
    """

    return await connection.execute_query_dict(query)
