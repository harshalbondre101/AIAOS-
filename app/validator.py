from typing import Tuple
from app.query import check_user_exist
from app.utils import OrderUtils


class Validator:
    """Validator class.

    ...

    Methods
    -------

    validate_create_order_request():
        Validate the Create Order request

    validate_create_user_request():
        Validate the Create User request

    validate_get_random_username_request():
        Validate the Get Random Username request

    validate_update_username_request():
        Validate the Update Username request

    validate_order_filtering_request():
        Validate the Order Filtering request

    validate_order_finish_request():
        Validate the Order Finish request

    validate_order_cancel_request():
        Validate the Order Cancel request

    validate_order_refund_request():
        Validate the Order Refund request

    validate_item_finish_request():
        Validate the Item Finish request

    validate_item_cancel_request():
        Validate the Item Cancel request
    """

    @staticmethod
    def validate_create_order_request(raw_data: dict) -> dict:
        """Validate the Create Order Request

        ...

        Parameters
        ----------
        `raw_data` (dict):
            A raw data retrieved from request.json

        Returns
        -------

        `data` (dict)
            A dictionary storing validated data
        """

        data = {
            "order_table": raw_data["order_table"],
            "order_type": raw_data["order_type"],
            "order_items": raw_data["order_items"],
            "time_spent": raw_data["time_spent"]
        }

        # User is optional
        try:
            data["user_id"] = raw_data["user"]["id"]
            data["user_point"] = raw_data["user"]["points"]
        except KeyError:
            data["user_id"] = None
            data["user_point"] = None

        # Order_type must be in ["dine_in", "take_away"]
        if data["order_type"] not in OrderUtils.available_order_types():
            raise Exception(
                "order_type is invalid: must in dine_in or take_away")

        # order_table must in range [1, max_table]
        if not str(data["order_table"]).isnumeric():
            raise Exception("order_table is invalid: must be an integer")

        order_table = int(data["order_table"])

        # Dine_in table must in range [1, MAX_TABLE]
        if data["order_type"] == OrderUtils.DINEIN_ORDER_TYPE:
            if order_table < 1 or order_table > raw_data["MAX_TABLE"]:
                raise Exception(
                    f"order_table is invalid: must be in range [1, {raw_data['MAX_TABLE']}]")

        # Dine_in table (code) must in range [0, inf]
        elif data["order_type"] == OrderUtils.TAKEAWAY_ORDER_TYPE:
            if order_table < 0:
                raise Exception(
                    f"order_table is invalid: must be in range [0, inf]")

        # Order must have some items, not an empty list
        if len(data["order_items"]) == 0:
            raise Exception("order_items is invalid: must have items")

        # Items inside order must not empty and must meaningful
        for item in data["order_items"]:
            # Item name's length must > 0
            if (item.get("name", None) is None) or (len(item["name"]) == 0):
                raise Exception("item_name is not valid: must have")

            # Quantity must be an integer and > 0
            if item.get("quantity", None) is None:
                raise Exception("item_quantity is not valid: must have")

            try:
                item_quantity = int(item["quantity"])
            except ValueError:
                raise Exception(
                    "item_quantity is not valid: must be an integer")
            if item_quantity <= 0:
                raise Exception(
                    "item_quantity is not valid: must greater than 0")

            # Price must be greater or equals 0
            if (item.get("price", None) is None):
                raise Exception("item_price is not valid: must have")
            try:
                item_price = float(item["price"])
            except ValueError:
                raise Exception("item_price is not valid: must be a float")
            if (item_price < 0):
                raise Exception(
                    "item_price is not valid: must be greater or equals 0")

        # User must exist
        if data["user_id"] is not None:
            if not check_user_exist(data["user_id"]):
                raise Exception("user_id not exist")

        # time_spent must be a numeric
        if not data["time_spent"].isnumeric():
            raise Exception("time_spent not valid: must be in seconds")
        data["buttons_clicked"] = raw_data["buttons_clicked"]
        data["buttons_category"] = raw_data["buttons_category"]
        return data

    @staticmethod
    def validate_create_user_request(raw_data: dict) -> str:
        """Validate the Create User Request

        ...

        Parameters
        ----------
        `raw_data` (dict):
            A raw data retrieved from request.json

        Returns
        -------

        `phone_number` (str)
            Validated phone number
        """

        phone_number = raw_data["phone_number"]

        if not phone_number.isnumeric():
            raise Exception("phone_number is not valid")

        return phone_number

    @staticmethod
    def validate_get_random_username_request(raw_data: dict) -> int:
        """Validate the Get Random Username Request

        ...

        Parameters
        ----------
        `raw_data` (dict):
            A raw data retrieved from request.json

        Returns
        -------

        `max_results` (int)
            Validated "maximum results"
        """

        max_results = raw_data["max_results"]

        if not str(max_results).isnumeric():
            raise Exception("max_results must be numeric")

        if int(max_results) < 1:
            raise Exception("max_results must have at least 1 result")

        return max_results

    @staticmethod
    def validate_update_username_request(raw_data: dict) -> Tuple[str, str]:
        """Validate the Update Username Request

        ...

        Parameters
        ----------
        `raw_data` (dict):
            A raw data retrieved from request.json

        Returns
        -------

        user_id, user_name (Tuple[str, str])
            Validated user_id and user_name
        """

        user_id = raw_data["user_id"]
        user_name = raw_data["user_name"]

        if len(user_name) == 0:
            raise Exception("user_name cannot be blank")

        return user_id, user_name

    @staticmethod
    def validate_order_filtering_request(raw_data: dict) -> dict:
        """Validate the Order Filtering Request

        ...

        Parameters
        ----------
        `raw_data` (dict):
            A raw data retrieved from request.json

        Returns
        -------

        `data` (dict)
            A dictionary storing validated data
        """

        start_date = raw_data["start_date"]
        end_date = raw_data["end_date"]
        table_list = raw_data["table_list"]
        mode_list = raw_data["mode_list"]
        status_list = raw_data["status_list"]

        if start_date > end_date:
            raise Exception("Start date is always before or equals to end date")

        data = {
            "start_date": start_date,
            "end_date": end_date,
            "table_list": table_list,
            "mode_list": mode_list,
            "status_list": status_list
        }

        return data

    @staticmethod
    def validate_order_finish_request(raw_data: dict) -> dict:
        """Validate the Order Finish Request

        ...

        Parameters
        ----------
        `raw_data` (dict):
            A raw data retrieved from request.json

        Returns
        -------

        `order_id` (int)
            Validated order_id
        """

        order_id = raw_data["order_id"]

        # Must have an order_id and it must be an integer
        if len(str(order_id)) == 0 or not str(order_id).isnumeric():
            raise Exception("order_id is not valid")

        return order_id

    @staticmethod
    def validate_order_cancel_request(raw_data: dict) -> dict:
        """Validate the Order Cancel Request

        ...

        Parameters
        ----------
        `raw_data` (dict):
            A raw data retrieved from request.json

        Returns
        -------

        `order_id` (int)
            Validated order_id
        """
        print("Validation")
        print(f"Raw data : {raw_data}")
        order_id = raw_data["order_id"]
        print(f"Order id : {order_id}")
        # Must have an order_id and it must be an integer
        if len(str(order_id)) == 0 or not str(order_id).isnumeric():
            raise Exception("order_id is not valid")

        return order_id

    @staticmethod
    def validate_order_refund_request(raw_data: dict) -> dict:
        """Validate the Order Refund Request

        ...

        Parameters
        ----------
        `raw_data` (dict):
            A raw data retrieved from request.json

        Returns
        -------

        `order_id` (dict)
            Validated order_id
        """

        # Must have the correct PINCODE
        pincode = raw_data["pincode"]

        if pincode != raw_data["system_pincode"]:
            raise Exception("Wrong pincode")

        # Must have an order_id and it must be an integer
        order_id = raw_data["order_id"]

        if len(str(order_id)) == 0 or not str(order_id).isnumeric():
            raise Exception("order_id is not valid")

        return order_id
