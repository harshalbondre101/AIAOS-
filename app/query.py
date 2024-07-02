from datetime import datetime

from flask import current_app
from psycopg2.extras import DictCursor, RealDictCursor

from app.cache import cache
from app.db import *
from app.utils import Utils, OrderUtils


def insert_order(data: dict) -> int:
    """Insert an order into the database

    ...

    Parameters
    ----------
    `data` (dict):
        The order's data to store:

            - `order_mode` (str):
                either "take_away" or "dine_in:

            - `order_creation_date` (str):
                current date, in string (use `datetime.now().strftime("%d/%m/%Y %H:%M:%S")`)

            - `order_table` (int): 
                order's table (int

            - `time_spent` (int): 
                time spent to order (in seconds, integer)

            - `user_id` (int): 
                id of the user.

            - `user_point` (float):
                points to update for the user

    Returns
    -------
    `new_order_id` (int):
        id of the newly-created order
    """

    db = get_db()

    # Get current date
    current_date = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    with db.cursor() as cur:
        cur.execute(
            """INSERT INTO orders (
                order_mode, 
                order_creation_date, 
                order_finish_date, 
                user_id, 
                order_table, 
                time_spent, 
                user_point, 
                order_status,
                buttons,
                buttons_category
            ) VALUES (
                %(order_mode)s, 
                %(order_creation_date)s, 
                %(order_finish_date)s, 
                %(user_id)s, 
                %(order_table)s, 
                %(time_spent)s, 
                %(user_point)s, 
                %(order_status)s,
                %(button)s,
                %(button_category)s
            ) 
            RETURNING id""",
            {"order_mode": data["order_type"],
             "order_creation_date": current_date,
             "order_finish_date": current_date,
             "user_id": data["user_id"],
             "order_table": data["order_table"],
             "time_spent": data["time_spent"],
             "user_point": data["user_point"],
             "order_status": OrderUtils.IN_PROGRESS_ORDER_STATUS,
             "button" : data["buttons_clicked"],
             "button_category" : data["buttons_category"]}),

        new_order_id = cur.fetchone()[0]

        list_items = []
        for item in data["order_items"]:
            this_item = (
                new_order_id, item["name"],
                item["quantity"],
                item["price"],
                OrderUtils.IN_PROGRESS_ITEM_STATUS)
            list_items.append(this_item)

        cur.executemany(
            "INSERT INTO orders_items (order_id, item_name, item_quantity, item_price, item_status) VALUES (%s, %s, %s, %s, %s)",
            list_items)

        db.commit()

    return new_order_id


def get_order(order_id: int) -> dict:
    """Get an order from order id

    ...

    Parameters
    ----------
    `order_id` (int):
        id of the order to get.

    Returns
    -------
    `order_detail` (dict):
        Detail of the order.

    """

    db = get_db()

    with db.cursor(cursor_factory=DictCursor) as cur:
        cur.execute("""SELECT
            orders.id as order_id,
            orders.order_table,
            orders.order_status,
            orders.order_creation_date,
            orders.order_finish_date,
            orders.order_mode,
            orders.user_point,
            orders.user_id,
            json_agg(json_build_object(
                'item_id', orders_items.item_id,
                'item_name', orders_items.item_name, 
                'item_quantity', orders_items.item_quantity,
                'item_status', orders_items.item_status)) as order_items
        FROM orders 
        LEFT JOIN orders_items
        ON orders.id = orders_items.order_id 
        WHERE orders.id = %(order_id)s
        GROUP BY orders.id
        """, {
            "order_id": order_id
        })

        order_detail = dict(cur.fetchone())

        # Format to string (with defined timezone)
        order_detail["order_creation_date"] = order_detail["order_creation_date"].astimezone(
            current_app.config["TIMEZONE"]).strftime("%d/%m/%Y %H:%M:%S")
        order_detail["order_finish_date"] = order_detail["order_finish_date"].astimezone(
            current_app.config["TIMEZONE"]).strftime("%d/%m/%Y %H:%M:%S")

    return order_detail


def get_table_orders(table: int) -> list:
    """Get orders of a table

    ...

    Parameters
    ----------
    `table` (int):
        id of the table to get

    Returns
    -------
    `return_group` (list):
        List of orders of the table.
    """
    db = get_db()

    with db.cursor(cursor_factory=DictCursor) as cur:
        cur.execute("""
            SELECT
                orders.id,
                orders.order_creation_date,
                orders.order_mode,
                orders.buttons,
                orders_items.item_id,
                orders_items.item_name,
                orders_items.item_quantity,
                orders_items.item_status
            FROM orders JOIN orders_items
            ON orders.id = orders_items.order_id 
            WHERE orders.order_table=%(table)s 
            AND orders.order_status=%(in_progress_order_status)s 
            AND orders.order_mode=%(dinein_mode)s
            ORDER BY orders.id ASC
        """, {
            "table": table,
            "in_progress_order_status": OrderUtils.IN_PROGRESS_ORDER_STATUS,
            "dinein_mode": OrderUtils.DINEIN_ORDER_TYPE,
        })

        tables = [dict(row) for row in cur.fetchall()]
        # print(tables)
        group_by_order_table = {}
        for item in tables:
            group_by_order_table.setdefault(
                table, []).append(
                {"order_id": item["id"],
                 "order_creation_date":
                 item["order_creation_date"].astimezone(
                     current_app.config["TIMEZONE"]).strftime(
                     "%d/%m/%Y %H:%M:%S"),
                 "order_mode": item["order_mode"],
                 "buttons" : tuple(item["buttons"])})
        # print("group_by_order_table : ",group_by_order_table)
        group_by_order_item = {}
        for item in tables:
            group_by_order_item.setdefault(item["id"], []).append({
                "id": item["item_id"],
                "name": item["item_name"],
                "quantity": item["item_quantity"],
                "status": item["item_status"],
            })

        return_group = []

        for _, value in group_by_order_table.items():
            # print('value : ',value)
            group_by_order_table_clean = [
                dict(t) for t in {tuple(d.items()) for d in value}]

            for order in group_by_order_table_clean:
                order["order_items"] = group_by_order_item[order["order_id"]]

            true_ordered_group = sorted(
                group_by_order_table_clean, key=lambda d: d["order_id"])

            return_group.append(true_ordered_group)
        # print('return group : ', return_group)
    return return_group


def get_take_away_orders() -> list:
    """Get all takeaway orders

    ...

    Parameters
    ----------
    None

    Returns
    -------
    `return_records` (list):
        List of takeaway orders
    """
    db = get_db()

    with db.cursor(cursor_factory=DictCursor) as cur:
        cur.execute("""SELECT
            orders.id as order_id,
            orders.order_table,
            orders.order_status,
            orders.order_creation_date,
            orders.order_finish_date,
            orders.order_mode,
            orders.user_id,
            json_agg(json_build_object(
                'item_id', orders_items.item_id,
                'item_name', orders_items.item_name, 
                'item_quantity', orders_items.item_quantity,
                'item_status', orders_items.item_status)) as order_items
        FROM orders 
        LEFT JOIN orders_items
        ON orders.id = orders_items.order_id 
        WHERE orders.order_status=%(in_progress_order_status)s
        AND orders.order_mode=%(takeaway_mode)s
        GROUP BY orders.id
        ORDER BY orders.id ASC""", {
            "in_progress_order_status": OrderUtils.IN_PROGRESS_ORDER_STATUS,
            "takeaway_mode": OrderUtils.TAKEAWAY_ORDER_TYPE,
        })

        records = [dict(row) for row in cur.fetchall()]

        return_records = []
        for record in records:
            current_record = record
            current_record["order_creation_date"] = record["order_creation_date"].astimezone(
                current_app.config["TIMEZONE"]).strftime("%d/%m/%Y %H:%M:%S")
            current_record["user_name"] = get_user_name(
                user_id=current_record["user_id"]) if current_record["user_id"] is not None else "Guest"

            return_records.append(current_record)

        return return_records


def get_table_in_progress_orders(max_table: int) -> dict:
    """Get in_progress table orders from the database

    ...

    Parameters
    ----------
    `max_table` (int):
        Total tables of the restaurant 

    Returns
    -------
    `group_by_order_table` (dict):
        Dictionary of tables, each table with its items.
    """
    db = get_db()

    with db.cursor(cursor_factory=DictCursor) as cur:
        cur.execute("""SELECT
            orders.order_table,
            orders.id
        FROM orders JOIN orders_items
        ON orders.id = orders_items.order_id 
        WHERE orders.order_status=%(in_progress_order_status)s
        AND orders.order_mode=%(dinein_mode)s
        ORDER BY orders.id ASC""", {
            "in_progress_order_status": OrderUtils.IN_PROGRESS_ORDER_STATUS,
            "dinein_mode": OrderUtils.DINEIN_ORDER_TYPE,
        })

        tables = [dict(row) for row in cur.fetchall()]

        group_by_order_table = {}
        for item in tables:
            group_by_order_table.setdefault(
                item["order_table"],
                []).append(
                item["id"])

        for i in range(1, max_table + 1):
            if group_by_order_table.get(i, None) is None:
                group_by_order_table[i] = []
            else:
                group_by_order_table[i] = sorted(
                    list(set(group_by_order_table[i])))

        group_by_order_table = dict(sorted(group_by_order_table.items()))

    return group_by_order_table


@cache.memoize(timeout=10)
def get_all_record_distinct_tables() -> list:
    """Get all distinct table from order list.

    ...

    Parameters
    ----------
    None

    Returns
    -------
    `records` (list):
        List of distict table recorded.
    """
    db = get_db()

    with db.cursor() as cur:
        cur.execute("""SELECT DISTINCT 
            orders.order_table
            FROM orders 
            ORDER BY orders.order_table""")

        records = [item[0] for item in cur.fetchall()]

    return records


def get_order_items(order_id: int) -> list:
    """Get items of an order

    ...

    Parameters
    ----------
    `order_id` (int):
        id of the order to get items

    Returns
    -------
    `order_items` (list):
        List of items belong to that order
    """
    db = get_db()

    with db.cursor(cursor_factory=DictCursor) as cur:
        cur.execute("""SELECT
            orders_items.item_id as id,
            orders_items.item_name as name,
            orders_items.item_status as status,
            orders_items.item_price as price,
            orders_items.item_quantity as quantity
        FROM orders_items WHERE order_id=%(order_id)s
        """, {
            "order_id": order_id
        })

        order_items = [dict(row) for row in cur.fetchall()]

    return order_items


@cache.memoize(timeout=10)
def get_orders_in_range(
        start_date: str, end_date: str, table_list: str = "", mode_list: str = "",
        status_list: str = "") -> list:
    """Get orders in a range of date

    ...

    Parameters
    ----------
    `start_date` (str):
        Start "Finish" date of the range (a string with `DD/MM/YYYY` format)
    `end_date` (str):
        End "Finish" date of the range (a string with `DD/MM/YYYY` format)
    `table_list` (str) - optional:
        A list but in string, of table ids (e.g. `[1, 3, 5, ..]` - get this with jQuery.text() method) 
    `mode_list` (str) - optional:
        A list but in string, of modes (e.g. `["dine_in", "take_away"]` - get this with jQuery.text() method) 
    `status_list` (str) - optional:
        A list but in string, of statuses (e.g. `["0", "1", ..etc]` - get this with jQuery.text() method)

    Returns
    -------
    `return_records` (list):
        List of orders in the previous range.
    """

    db = get_db()

    # Build the filter query
    base_query = """SELECT
                orders.order_table,
                orders.id as order_id,
                orders.order_status,
                orders.order_creation_date,
                orders.order_finish_date,
                orders.order_mode,
                json_agg(json_build_object(
                    'item_name', orders_items.item_name, 
                    'item_price', orders_items.item_price,
                    'item_quantity', orders_items.item_quantity,
                    'item_status', orders_items.item_status)) as order_items
            FROM orders 
            LEFT JOIN orders_items
            ON orders.id = orders_items.order_id 
            WHERE orders.order_finish_date::date >= %(start_date)s
            AND orders.order_finish_date::date <= %(end_date)s
            """

    base_data = {
        "start_date": start_date,
        "end_date": end_date
    }

    if len(table_list) > 0:
        base_query += """
            AND orders.order_table = ANY(%(table_list)s::int[])
        """

        base_data["table_list"] = table_list

    if len(mode_list) > 0:
        base_query += """
            AND orders.order_mode = ANY(%(mode_list)s)
        """

        base_data["mode_list"] = mode_list

    if len(status_list) > 0:
        base_query += """
            AND orders.order_status = ANY(%(status_list)s::available_order_status[])
        """

        base_data["status_list"] = status_list

    base_query += """
        GROUP BY orders.id
        ORDER BY orders.order_finish_date DESC
    """

    with db.cursor(cursor_factory=DictCursor) as cur:
        cur.execute(base_query, base_data)

        records = [dict(row) for row in cur.fetchall()]

        return_records = []
        for item in records:
            current_item = item
            current_item["order_creation_date"] = item["order_creation_date"].astimezone(
                current_app.config["TIMEZONE"]).strftime("%d/%m/%Y %H:%M:%S")

            if item["order_finish_date"] is not None:
                current_item["order_finish_date"] = item["order_finish_date"].astimezone(
                    current_app.config["TIMEZONE"]).strftime("%d/%m/%Y %H:%M:%S")
            else:
                current_item["order_finish_date"] = None

            return_records.append(current_item)

        return return_records


@cache.memoize(timeout=10)
def get_best_seller_items(max_items=5) -> list:
    """Get the best seller items.

    Args:
        max_items (int, optional): max best seller items. Defaults to 5.

    Returns:
        list: list of best seller items.
    """

    db = get_db()

    with db.cursor(cursor_factory=DictCursor) as cur:
        cur.execute("""
            SELECT 
                orders_items.item_name as name,
                orders_items.item_price as price,
                orders_items.item_quantity as quantity,
                SUM(orders_items.item_price * orders_items.item_quantity) as sales,
                orders_items.item_status as status
            from orders_items
            WHERE orders_items.item_status=%(finished_item_status)s
            GROUP BY name, price, quantity, status
            ORDER BY sales DESC
            LIMIT %(max_items)s
        """, {
            "max_items": max_items,
            "finished_item_status": OrderUtils.FINISHED_ITEM_STATUS
        })

        records = [dict(row) for row in cur.fetchall()]
        return records


def finish_order(order_id: int) -> str:
    """Finish the order (set status=1)

    ...

    Parameters
    ----------
    `order_id` (int) 
        id of the order to finish

    Returns
    -------
    `modified_date` (str)
        Modification date

    Exceptions
    ----------
    Exception thrown if order_id not found.
    """

    db = get_db()

    # Get current date
    modified_date = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    with db.cursor(cursor_factory=DictCursor) as cur:
        # Update
        cur.execute(
            """UPDATE orders SET (order_status, order_finish_date) = (%(finished_order_status)s, %(order_finish_date)s)
            WHERE id=%(order_id)s AND order_status=%(in_progress_order_status)s
            RETURNING orders.id, orders.user_id, orders.user_point
            """, {
                "finished_order_status": OrderUtils.FINISHED_ORDER_STATUS,
                "in_progress_order_status": OrderUtils.IN_PROGRESS_ORDER_STATUS,
                "order_id": order_id,
                "order_finish_date": modified_date
            })

        # If no row affected, throw error based on what happened
        try:
            order_info = dict(cur.fetchone())

        # No row affected due to order_id not found
        except TypeError:
            raise Exception("order_id not found")

        # Mark all items as finished, except canceled items
        cur.execute(
            """UPDATE orders_items SET item_status=%(finished_item_status)s
            WHERE order_id=%(order_id)s AND item_status=%(in_progress_item_status)s""", {
                "order_id": order_id,
                "in_progress_item_status": OrderUtils.IN_PROGRESS_ITEM_STATUS,
                "finished_item_status": OrderUtils.FINISHED_ITEM_STATUS
            })

        # Update point for the user
        if order_info["user_id"] is not None:
            cur.execute(
                """UPDATE users SET points=%(user_point)s
                WHERE users.id=%(user_id)s
                """, {
                    "user_id": order_info["user_id"],
                    "user_point": order_info["user_point"]
                })

        db.commit()

    return modified_date

def user_actions(order_id: int) -> str:
    db = get_db()
    with db.cursor() as cur:
        cur.execute(
            """SELECT users.name,users.phone_number,orders.buttons,orders.buttons_category
            FROM orders
            LEFT JOIN users 
            ON orders.user_id = users.id
            WHERE orders.id=%(order_id)s AND order_status=%(in_progress_order_status)s""", {
                "in_progress_order_status": OrderUtils.IN_PROGRESS_ORDER_STATUS,
                "order_id": order_id
            }
        )
        records = cur.fetchall()
    if records:
        # Assuming you want to return a list of buttons
        name,phone_number,buttons,buttons_category = records[0]
        # print(buttons)
        # print(buttons)
        return {"user_name": name, "phone_number" : phone_number, "buttons": buttons,"buttons_category" : buttons_category}
    else:
        return {"user_name": "", "phone_number" : "","buttons": [],"buttons_category" : []}


def cancel_order(order_id: int) -> str:
    """Cancel the order (set status=2)

    ...

    Parameters
    ----------
    `order_id` (int) 
        id of the order to finish

    Returns
    -------
    `modified_date` (str)
        the date when the order is canceled

    Exceptions
    ----------
    Exception thrown if order_id not found.
    """

    db = get_db()

    # Get current date
    modified_date = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    with db.cursor() as cur:
        cur.execute(
            """UPDATE orders 
            SET (order_status, order_finish_date) = (%(canceled_order_status)s, %(order_finish_date)s) 
            WHERE id=%(order_id)s AND order_status=%(in_progress_order_status)s
            RETURNING orders.id""", {
                "order_id": order_id,
                "canceled_order_status": OrderUtils.CANCELED_ORDER_STATUS,
                "in_progress_order_status": OrderUtils.IN_PROGRESS_ORDER_STATUS,
                "order_finish_date": modified_date,
            })

        # If no row affected, throw error based on what happened
        try:
            _ = cur.fetchone()[0]

        # No row affected due to order_id not found
        except TypeError:
            raise Exception("order_id not found")

        # Mark all items as canceled, even if they're finished or in progress.
        cur.execute(
            """UPDATE orders_items SET item_status=%(canceled_item_status)s
            WHERE order_id=%(order_id)s""", {
                "order_id": order_id,
                "canceled_item_status": OrderUtils.CANCELED_ITEM_STATUS,
            })

        db.commit()

    return modified_date


def refund_order(order_id: int) -> str:
    """Refund the order (set status=3)

    ...

    Parameters
    ----------
    `order_id` (int) 
        id of the order to finish

    Returns
    -------
    `modified_date` (str)
        the date when the action is success

    Exceptions
    ----------
    Exception thrown if order_id not found.
    """

    db = get_db()

    # Get current date
    modified_date = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    with db.cursor() as cur:
        cur.execute("""
            UPDATE orders SET (order_status, order_finish_date) = (%(refunded_order_status)s, %(order_finish_date)s)
            WHERE orders.id=%(order_id)s AND orders.order_status=%(finished_order_status)s
            RETURNING orders.id
        """, {
            "order_id": order_id,
            "finished_order_status": OrderUtils.FINISHED_ORDER_STATUS,
            "refunded_order_status": OrderUtils.REFUNDED_ORDER_STATUS,
            "order_finish_date": modified_date
        })

        # If no row affected, throw error based on what happened
        try:
            _ = cur.fetchone()[0]

        # No row affected due to order_id not found
        except TypeError:
            raise Exception("order_id not found")

        db.commit()

    return modified_date


def finish_item(item_id: int) -> int:
    """Mark/unmark an item as finished

    Parameters
    ----------
    `item_id` (int) 
        id of the item to finish

    Returns
    -------
    new_status (int):
        New status of the item after set
    """
    db = get_db()

    with db.cursor() as cur:
        cur.execute("""UPDATE orders_items 
        SET item_status = CASE item_status
            WHEN %(in_progress_item_status)s::available_item_status THEN %(finished_item_status)s::available_item_status
            WHEN %(finished_item_status)s::available_item_status THEN %(in_progress_item_status)s::available_item_status
            WHEN %(canceled_item_status)s::available_item_status THEN %(finished_item_status)s::available_item_status
        END
        FROM orders
        WHERE item_id=%(item_id)s 
        AND orders.order_status=%(in_progress_order_status)s
        AND orders.id = orders_items.order_id
        RETURNING item_status
        """, {
            "item_id": item_id,
            "in_progress_order_status": OrderUtils.IN_PROGRESS_ORDER_STATUS,
            "in_progress_item_status": OrderUtils.IN_PROGRESS_ITEM_STATUS,
            "finished_item_status": OrderUtils.FINISHED_ITEM_STATUS,
            "canceled_item_status": OrderUtils.CANCELED_ITEM_STATUS,
        })

        try:
            new_status = cur.fetchone()[0]
        except TypeError:
            raise Exception("This item does not belong to an ongoing order")

    db.commit()

    return new_status


def cancel_item(item_id: int) -> int:
    """Mark/unmark an item as canceled

    Parameters
    ----------
    `item_id` (int) 
        id of the item to cancel

    Returns
    -------
    new_status (int):
        New status of the item after set
    """

    db = get_db()

    with db.cursor() as cur:
        cur.execute("""UPDATE orders_items 
        SET item_status = CASE item_status
            WHEN %(in_progress_item_status)s::available_item_status THEN %(canceled_item_status)s::available_item_status
            WHEN %(finished_item_status)s::available_item_status THEN %(canceled_item_status)s::available_item_status
            WHEN %(canceled_item_status)s::available_item_status THEN %(in_progress_item_status)s::available_item_status
        END
        FROM orders
        WHERE item_id=%(item_id)s 
        AND orders.order_status=%(in_progress_order_status)s
        AND orders.id = orders_items.order_id
        RETURNING item_status
        """, {
            "item_id": item_id,
            "in_progress_order_status": OrderUtils.IN_PROGRESS_ORDER_STATUS,
            "finished_item_status": OrderUtils.FINISHED_ITEM_STATUS,
            "canceled_item_status": OrderUtils.CANCELED_ITEM_STATUS,
            "in_progress_item_status": OrderUtils.IN_PROGRESS_ITEM_STATUS,
        })

        try:
            new_status = cur.fetchone()[0]
        except TypeError:
            raise Exception("This item does not belong to an ongoing order")

    db.commit()

    return new_status


def get_or_create_user(phone_number: str) -> dict:
    """Get the user with a phone number, if not create a new one.

    ...

    Parameters
    ----------
    `phone_number` (str):
        5 last digits of the user's phone number

    Returns
    -------
    `user` (dict):
        A user profile with the previous phone number.

        - `id` (int): 
            user id
        - `name` (int):
            user name
        - `points` (float):
            user points
    """

    db = get_db()

    with db.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("""SELECT 
            id,
            name,
            points 
        FROM users
        WHERE phone_number=%(phone_number)s
        """, {
            "phone_number": phone_number
        })

        user = cur.fetchone()
        if user is None:
            # User does not exist, insert new user to the system.
            cur.execute("""INSERT INTO users (phone_number, name, points)
            VALUES (%(phone_number)s, NULL, 0)
            RETURNING id, name, points
            """, {
                "phone_number": phone_number
            })

            db.commit()

            user = cur.fetchone()

    return user


@cache.memoize(timeout=10)
def get_user_name(user_id: int) -> str:
    """
    Get a user name from an ID

    ...

    Parameters:
    -----------
    `user_id` (int):
        id of the user to get username

    Returns:
    --------
    `user_name` (str):
        the username of the user just get.
    """
    db = get_db()

    with db.cursor() as cur:
        cur.execute("""SELECT users.name
        FROM users
        WHERE users.id=%(user_id)s
        """, {
            "user_id": user_id
        })

        user_name = cur.fetchone()[0]

        # Username not set.
        if user_name is None:
            return Utils.DEFAULT_USERNAME

    return user_name


@cache.memoize(timeout=10)
def check_user_exist(user_id: int) -> bool:
    """Check if user exist.

    ...

    Parameters
    ----------
    `user_id` (int):
        id of the user to check

    Returns
    -------
    `status` (bool):
        User account's status, `true` if exist and `false` otherwise.
    """

    db = get_db()

    with db.cursor() as cur:
        cur.execute("""SELECT COUNT(id) FROM users WHERE users.id=%(user_id)s
        """, {
            "user_id": user_id
        })

        return cur.fetchone()[0] == 1


def update_user_name(user_id: int, user_name: str) -> None:
    """Update user name.

    ...

    Parameters
    ----------
    `user_id` (int):
        id of the user
    `user_name` (str):
        the name to change

    Returns
    -------
    None

    Exceptions
    ----------
    Exception thrown if no user affected (i.e. user_id not exist)
    """

    db = get_db()

    with db.cursor(cursor_factory=DictCursor) as cur:
        cur.execute("""UPDATE users SET name=%(user_name)s
        WHERE id=%(user_id)s
        RETURNING id
        """, {
            "user_name": user_name,
            "user_id": user_id
        })

        try:
            _ = cur.fetchone()[0]
        except TypeError:
            raise Exception("user_id not exist")

        db.commit()


@cache.memoize(timeout=5)
def get_user_history_stats() -> list:
    """Get the list of users history

    ...

    Parameters
    ----------
    None

    Returns
    -------
    `results` (list): list of ('user_name', 'user_phone', 'user_points', 'user_orders', 'user_spent')
    """

    db = get_db()

    with db.cursor(cursor_factory=DictCursor) as cur:
        cur.execute("""SELECT 
            users.name as user_name,
            users.phone_number as user_phone,
            users.points as user_points,
            count(distinct orders.id) as user_orders,
            sum(orders_items.item_quantity * orders_items.item_price) as user_spent
        FROM users
        JOIN orders ON orders.user_id = users.id
        JOIN orders_items ON orders_items.order_id = orders.id
        WHERE orders.order_status=%(finished_order_status)s
        AND orders_items.item_status=%(finished_item_status)s
        GROUP BY users.id
        ORDER BY user_points DESC
        """, {
            "finished_order_status": OrderUtils.FINISHED_ORDER_STATUS,
            "finished_item_status": OrderUtils.FINISHED_ITEM_STATUS,
        })

        results = [dict(item) for item in cur.fetchall()]

    return results


@cache.memoize(timeout=10)
def get_user_history_latest_order(user_id: int) -> list:
    """Get the latest order from the user.

    ...

    Parameters
    ----------
    `user_id` (int):
        id of the user

    Returns
    -------
    `return_record` (list):
        Tuple (id,).
    """

    db = get_db()

    with db.cursor() as cur:
        cur.execute("""SELECT orders.id
        FROM orders
        WHERE orders.user_id=%(user_id)s
        AND orders.order_status=%(finished_order_status)s
        ORDER BY orders.order_finish_date DESC
        LIMIT 1
        """, {
            "user_id": user_id,
            "finished_order_status": OrderUtils.FINISHED_ORDER_STATUS,
        })

        return_records = cur.fetchone()

    return return_records


@cache.memoize(timeout=10)
def insert_order_actions(data: dict) -> int:
    db = get_db()
    with db.cursor() as cur:
        cur.execute(
            """INSERT INTO order_actions (
                order_id, 
                menu_buttons,
                menu_total,
                upsell_buttons,
                upsell_total
                ) VALUES (
                %(order_id)s, 
                %(menu_buttons)s, 
                %(menu_total)s, 
                %(upsell_buttons)s, 
                %(upsell_total)s 
            ) 
            RETURNING id""",
            {"order_id": data["order_id"],
             "menu_buttons": data["menu_buttons"],
             "menu_total": data["menu_total"],
             "upsell_buttons": data["upsell_buttons"],
             "upsell_total": data["upsell_total"]})
    db.commit()
    return data["order_id"]
