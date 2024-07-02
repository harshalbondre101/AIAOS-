from typing import Tuple

from unique_names_generator import get_random_name

from app.query import *
from app.utils import OrderUtils, Utils

class GetOrder:
    @staticmethod
    def get_order_details(order_id: int) -> list:
        """Get details of a specific order by ID

        Parameters
        ----------
        order_id : int
            The ID of the order to retrieve

        Returns
        -------
        order_details : list
            The list of items with their names and quantities
        """
        order_details = get_order(order_id=order_id)
        order_items = order_details['order_items']
        
        formatted_order_items = [{'item_name': item['item_name'], 'quantity': item['item_quantity']} for item in order_items]
        
        return formatted_order_items


class TableService:
    """TableService class.

    ...

    Methods
    -------

    get_all_record_distinct_tables_service():
        Get all distinct table from order list
    """

    @staticmethod
    def get_all_record_distinct_tables_service() -> list:
        """Get all distinct table from order list.

        ...

        Parameters
        ----------
        None

        Returns
        -------
        `tables` (list):
            List of distict table recorded.
        """

        tables = get_all_record_distinct_tables()
        return tables


class OrderService:
    """OrderService class.

    ...

    Methods
    -------

    get_take_away_orders_service():
        Get all takeaway orders

    get_table_in_progress_orders_service():
        Get in_progress table orders from the database

    insert_new_order_service():
        Insert an order into the database, then return the newly-created order with its id

    get_table_orders_service():
        Get orders of a table

    get_orders_in_range_service():
        Get orders in a range of date

    finish_order_service():
        Finish the order (set status=1)

    cancel_order_service():
        Cancel the order (set status=2)

    refund_order_service():
        Refund the order (set status=3)
    """

    @staticmethod
    def get_take_away_orders_service() -> list:
        """Get all takeaway orders

        ...

        Parameters
        ----------
        None

        Returns
        -------
        `takeaway_orders` (list):
            List of takeaway orders
        """

        takeaway_orders = get_take_away_orders()
        return takeaway_orders

    @staticmethod
    def get_table_in_progress_orders_service(max_table: int) -> dict:
        """Get in_progress table orders from the database

        ...

        Parameters
        ----------
        `max_table` (int):
            Total tables of the restaurant 

        Returns
        -------
        `tables_in_progress` (dict):
            Dictionary of tables, each table with its items.
        """

        tables_in_progress = get_table_in_progress_orders(max_table=max_table)
        # print(tables_in_progress)
        return tables_in_progress

    @staticmethod
    def insert_new_order_service(data: dict) -> Tuple[dict, int]:
        """Insert an order into the database,
        then return the newly-created order with its id

        Args:
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

        Returns:
            Tuple[dict, int]:
                Data of the newly-created order and its id
        """
        # Create new order
        new_order_id = insert_order(data=data)

        if data["order_type"] == OrderUtils.DINEIN_ORDER_TYPE:
            # Get table's orders after insert this new order to send to dine_in panel
            current_table_data = get_table_orders(table=data["order_table"])

            return_data = {
                "order_type": data["order_type"],
                "data": {
                    "order_table": data["order_table"],
                    "table_data": current_table_data
                }
            }
        else:
            # Get order's data to send to send to take_away panel
            order_data = get_order(order_id=new_order_id)
            order_data["user_name"] = "Guest" if data["user_id"] is None else get_user_name(data["user_id"])

            return_data = {
                "order_type": data["order_type"],
                "data": {
                    "order_data": order_data
                }
            }

        return return_data, new_order_id

    @staticmethod
    def get_table_orders_service(table: int) -> list:
        """Get orders of a table

        ...

        Parameters
        ----------
        `table` (int):
            id of the table to get

        Returns
        -------
        `orders` (list):
            List of orders of the table.
        """

        orders = get_table_orders(table=table)
        # print('orders : ',orders)
        return orders

    @staticmethod
    def get_orders_in_range_service(data: dict) -> list:
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
        `orders` (list):
            List of orders in the previous range.
        """

        orders = get_orders_in_range(**data)
        return orders

    @staticmethod
    def finish_order_service(order_id: int) -> str:
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

        modified_date = finish_order(order_id=order_id)
        return modified_date
    
    @staticmethod
    def get_user_actions(order_id : int) -> str:
        actions = user_actions(order_id=order_id)
        return actions


    @staticmethod
    def cancel_order_service(order_id: int) -> str:
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

        modified_date = cancel_order(order_id=order_id)
        return modified_date

    @staticmethod
    def refund_order_service(order_id: int) -> str:
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

        modified_date = refund_order(order_id=order_id)
        return modified_date
    @staticmethod
    def insert_order_actions(actions : dict) -> int:
        order_id = insert_order_actions(actions)
        return order_id

class ItemService:
    """ItemService class.

    ...

    Methods
    -------

    cancel_item_service():
        Mark/unmark an item as finished

    finish_item_service():
        Mark/unmark an item as finished
    """

    @staticmethod
    def cancel_item_service(item_id: int) -> int:
        """Mark/unmark an item as canceled

        Parameters
        ----------
        `item_id` (int) 
            id of the item to cancel

        Returns
        -------
        `item_status` (int):
            New status of the item after set
        """

        item_status = cancel_item(item_id=item_id)
        return item_status

    @staticmethod
    def finish_item_service(item_id: int) -> int:
        """Mark/unmark an item as finished

        Parameters
        ----------
        `item_id` (int) 
            id of the item to finish

        Returns
        -------
        `item_status` (int):
            New status of the item after set
        """

        item_status = finish_item(item_id=item_id)
        return item_status


class UserService:
    """UserService class.

    ...

    Methods
    -------

    generate_names_list_service():
        Generate random name list

    update_user_name_service():
        Update user name.

    get_or_create_user_service():
        Get the user with a phone number, if not create a new one

    get_user_history_stats_service():
        Get the list of users history

    get_user_order_history_service():
        Get the latest order from the user
    """

    @staticmethod
    def generate_names_list_service(max_results: int) -> list:
        """Generate random name list with max results

        Args:
            `max_results` (int):
                Maximum results

        Returns:
            `name_list` (list):
                List of random name generated
        """

        name_list = [get_random_name() for _ in range(max_results)]
        return name_list

    @staticmethod
    def update_user_name_service(user_id: int, user_name: str) -> None:
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

        _ = update_user_name(user_id=user_id, user_name=user_name)
        return _

    @staticmethod
    def get_or_create_user_service(phone_number: str) -> dict:
        """Get the user with a phone number, if not create a new one.

        ...

        Parameters
        ----------
        `phone_number` (str):
            5 last digits of the user's phone number

        Returns
        -------
        `new_user` (dict):
            A user profile with the previous phone number.

            - `id` (int): 
                user id
            - `name` (int):
                user name
            - `points` (float):
                user points
        """

        new_user = get_or_create_user(phone_number=phone_number)
        return new_user

    @staticmethod
    def get_user_history_stats_service() -> list:
        """Get the list of users history

        ...

        Parameters
        ----------
        None

        Returns
        -------
        `users_stat` (list): list of ('user_name', 'user_phone', 'user_points', 'user_orders', 'user_spent')
        """

        users_stat = get_user_history_stats()
        return users_stat

    @staticmethod
    def get_user_order_history_service(user: dict, max_items: int) -> list:
        """Get the latest order from the user.

        ...

        Parameters
        ----------
        `user_id` (int):
            id of the user

        Returns
        -------
        `latest_order_items` (list):
            List of (item name, item price), sorted by item price.
        """

        latest_order = get_user_history_latest_order(user_id=user["id"])

        # Get finished items (name and price)
        if latest_order is not None:
            latest_order_items = get_order_items(order_id=latest_order)

            # Filter out items finished
            recommended_items = [{"name": item["name"], "price": item["price"]}
                                 for item in latest_order_items if item["status"] == OrderUtils.FINISHED_ITEM_STATUS]

            # Sort descending to get most expensive items first.
            recommended_items.sort(key=lambda x: x["price"], reverse=True)

        # Recommends best seller items - new users only
        else:
            best_seller_items = get_best_seller_items(max_items=max_items)

            # We don't need to filter out finished items and sorting here,
            # since it's been done in the query phase.
            recommended_items = [{"name": item["name"], "price": item["price"]}
                                 for item in best_seller_items]

        return recommended_items
