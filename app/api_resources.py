from typing import Tuple

from flask import current_app, request
from flask_restful import Resource

from app.services import ItemService, OrderService, UserService
from app.validator import Validator
import pandas as pd
from flask import send_file
import os


class UserNameAPI(Resource):
    """API to handle tasks related to the User name

    ...

    Methods
    -------
    get():
        Handle UsernameRandomGenerator API GET request from the user client

    post():
        Handle UsernameChanging API POST request from the user client
    """

    def get(self) -> Tuple[dict, int]:
        """Handle UsernameRandomGenerator API GET request from the client

        ...

        Parameters
        ----------
        None

        Returns
        -------
        `response` (Tuple[dict, int]):

            In case of successfully: a dictionary with one key `name_list` and HTTP `status_code` 200.
            - `name_list` (list):
                list of generated names
            - `status_code` (int):
                Successful code: 200
        """

        try:
            raw_data = request.get_json(force=True)

            max_results = Validator.validate_get_random_username_request(
                raw_data=raw_data)

            name_list = UserService.generate_names_list_service(
                max_results=max_results)
        except Exception as e:
            return {
                "message": "Cannot generate names",
                "error": str(e)
            }, 400

        return {
            "name_list": name_list
        }, 200

    def post(self) -> Tuple[dict, int]:
        """Handle User API POST request from the client

        ...

        Parameters
        ----------
        None

        Returns
        -------
        `response` (Tuple[dict, int]):

            In case of successfully: `message` and HTTP `status_code` 200.
            - `message` (str):
                success message
            - `status_code` (int):
                Successful code: 200

            In case of failed: Include a `failed` response dictionary and HTTP `status_code` 400.
            - `failed` (dict):
                Include `message`  and `error` - error details.
            - `status_code` (int):
                Fails code: 400
        """

        try:
            raw_data = request.get_json(force=True)

            user_id, user_name = Validator.validate_update_username_request(
                raw_data=raw_data)

            _ = UserService.update_user_name_service(
                user_id=user_id, user_name=user_name)
        except Exception as e:
            return {
                "message": "Cannot set new name",
                "error": str(e)
            }, 400

        return {
            "message": "Successfully changed the user's name"
        }, 200


class GetUserAPI(Resource):
    """API to get  User from the system

    ...

    Methods
    -------
    get():
        Handle User API GET request to get statistics of all users.
    post():
        Handle User API POST request from the user client to get details of one user
    """

    def get(self) -> Tuple[dict, int]:
        """Handle User API GET request from the client

        ...

        Parameters
        ----------
        None

        Returns
        -------
        `response` (Tuple[dict, int]):

            In case of successfully: Include a `user_history` response dict and HTTP `status_code` 200.
            - `user_history` (dict):
                user object list
            - `status_code` (int):
                Successful code: 200

            In case of failed: Include a `failed` response dictionary and HTTP `status_code` 400.
            - `failed` (dict):
                Include `message`  and `error` - error details.
            - `status_code` (int):
                Fails code: 400
        """

        user_list = UserService.get_user_history_stats_service()
        return {
            "user_list": user_list
        }, 200

    def post(self) -> Tuple[dict, int]:
        """Handle User API POST request from the client

        ...

        Parameters
        ----------
        None

        Returns
        -------
        `response` (Tuple[dict, int]):

            In case of successfully: Include a `user` response dictionary and HTTP `status_code` 200.
            - `user` (dict):
                user object
            - `status_code` (int):
                Successful code: 200

            In case of failed: Include a `failed` response dictionary and HTTP `status_code` 400.
            - `failed` (dict):
                Include `message`  and `error` - error details.
            - `status_code` (int):
                Fails code: 400
        """

        try:
            raw_data = request.get_json(force=True)

            phone_number = Validator.validate_create_user_request(
                raw_data=raw_data)

            user = UserService.get_or_create_user_service(
                phone_number=phone_number)

            # Get latest items.
            latest_order_items = UserService.get_user_order_history_service(
                user=user, max_items=current_app.config["MAX_RECOMMEND_ITEMS"])

        except Exception as e:
            return {
                "message": "Failed to get user",
                "error": str(e)
            }, 400

        return {
            "user": user,
            "latest_items": latest_order_items
        }, 200


class CreateOrderAPI(Resource):
    """API to create an order

    ...

    Attributes
    ----------
    socket_io:
        Handle of the socket_io instance created in main.py

    Methods
    -------
    post():
        Handle Create Order API POST request from the client
    """

    def __init__(self, **kwargs) -> None:
        self.socket_io = kwargs.get("socket_io", None)

    def post(self) -> Tuple[dict, int]:
        """Handle Create Order API POST request from the client

        ...

        Parameters
        ----------
        None

        Returns
        -------
        `response` (Tuple[dict, int]):

            In case of successfully: Include a `message` response string and HTTP `status_code` 200.
            Also, this API will send a socket request to the frontend to update.
            - `message` (string):
                A message state that operation is successfully executed.
            - `new_order_id` (int):
                ID of the new order
            - `status_code` (int):
                Successful code: 200

            In case of failed: Include a `failed` response dictionary and HTTP `status_code` 400.
            - `failed` (dict):
                Include `message`  and `error` - error details.
            - `status_code` (int):
                Fails code: 400
        """

        try:
            raw_data = request.get_json(force=True)
            print("request : ",raw_data)
            raw_data["MAX_TABLE"] = current_app.config["MAX_TABLE"]

            data = Validator.validate_create_order_request(raw_data=raw_data)
            # print(data)
            # Create a new order
            return_data, new_order_id = OrderService.insert_new_order_service(
                data)

            # Then ping the frontend with the new info
            self.socket_io.send(data=return_data)
        except Exception as e:
            return {
                "message": "Failed to create order",
                "error": str(e)
            }, 400

        return {
            "message": "Create order successfully",
            "new_order_id": new_order_id
        }, 200


class GetSingleTableAPI(Resource):
    """API to get a table's items

    ...

    Methods
    -------
    post():
        Handle Get Single Table API POST request from the client
    """

    def post(self) -> Tuple[dict, int]:
        """Handle Create Order API POST request from the client

        ...

        Parameters
        ----------
        None

        Returns
        -------
        `response` (Tuple[dict, int]):

            In case of successfully: Include a `response_dict` response dict and HTTP `status_code` 200.
            - `response_dict` (dict):
                Including `table_id` and list of orders `order_list` belongs to that table.
            - `status_code` (int):
                Successful code: 200

            In case of failed: Include a `failed` response dictionary and HTTP `status_code` 400.
            - `failed` (dict):
                Include `message`  and `error` - error details.
            - `status_code` (int):
                Fails code: 400
        """

        try:
            raw_data = request.get_json(force=True)

            table_id = raw_data["table_id"]

            order_list = OrderService.get_table_orders_service(table=table_id)

        except Exception as e:
            return {
                "message": "Failed to get order",
                "error": str(e)
            }, 400

        return {
            "table": table_id,
            "order_list": order_list
        }, 200


class GetOrderInRangeAPI(Resource):
    """API to get orders in a date range

    ...

    Methods
    -------
    post():
        Handle Get Order In Range API POST request from the client
    """

    def post(self) -> Tuple[dict, int]:
        """Handle Get Order In Range API POST request from the client

        ...

        Parameters
        ----------
        None

        Returns
        -------
        `response` (Tuple[dict, int]):

            In case of successfully: Include a `order_list` response list and HTTP `status_code` 200.
            - `order_list` (list):
                Orders list in that range.
            - `status_code` (int):
                Successful code: 200

            In case of failed: Include a `failed` response dictionary and HTTP `status_code` 400.
            - `failed` (dict):
                Include `message`  and `error` - error details.
            - `status_code` (int):
                Fails code: 400
        """

        try:
            raw_data = request.get_json(force=True)

            data = Validator.validate_order_filtering_request(raw_data=raw_data)

            order_list = OrderService.get_orders_in_range_service(data)

        except Exception as e:
            return {
                "message": "Failed to get order",
                "error": str(e)
            }, 400

        return {
            "order_list": order_list
        }, 200


class FinishOrderAPI(Resource):
    """API to finish an order

    ...

    Methods
    -------
    post():
        Handle Finish Order API POST request from the client
    """

    def post(self) -> Tuple[dict, int]:
        """Handle Finish Order API POST request from the client

        ...

        Parameters
        ----------
        None

        Returns
        -------
        `response` (Tuple[dict, int]):

            In case of successfully: Include a `message` response string and HTTP `status_code` 200.
            - `message` (string):
                A message state that operation is successfully executed.
            - `modified_date` (string):
                Datetime that action is success
            - `status_code` (int):
                Successful code: 200

            In case of failed: Include a `failed` response dictionary and HTTP `status_code` 400.
            - `failed` (dict):
                Include `message`  and `error` - error details.
            - `status_code` (int):
                Fails code: 400
        """

        try:
            raw_data = request.get_json(force=True)



            order_id = Validator.validate_order_finish_request(
                raw_data=raw_data)

            modified_date = OrderService.finish_order_service(order_id=order_id)
        except Exception as e:
            return {
                "message": "Failed to set order status to finish",
                "error": str(e)
            }, 400

        return {
            "message": "Finish order successfully",
            "modified_date": modified_date
        }, 200

class OrderActionsAPI(Resource):

    def post(self) -> Tuple[dict, int]:

        try:
            if request.is_json:
                # JSON data
                raw_data = request.get_json(force=True)
            else:
                # Form data
                raw_data = request.form.to_dict()
        

            order_id = Validator.validate_order_finish_request(
                raw_data=raw_data)

            user_actions = OrderService.get_user_actions(order_id=order_id)
            if user_actions["user_name"]:
                user_actions["buttons_category"].insert(0,"Username")
                user_actions["buttons"].insert(0,user_actions["user_name"])
            elif user_actions["phone_number"]:
                user_actions["buttons_category"].insert(0,"User Phone Number")
                user_actions["buttons"].insert(0,user_actions["phone_number"])
            else:
                user_actions["buttons_category"].insert(0,"User")
                user_actions["buttons"].insert(0,"Guest")
            
            df = pd.DataFrame({"buttons_category" : user_actions["buttons_category"],'buttons' : user_actions['buttons']})
            df = df.transpose()
            file_directory = os.path.join(os.getcwd(), 'app')
            excel_file = os.path.join(file_directory, "user_actions.xlsx")
            # print(excel_file)
            df.to_excel(excel_file,index=False)
            return send_file(excel_file,as_attachment=True, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        except Exception as e:
            return {
                "message": "Failed to get user actions",
                "error": str(e)
            }, 400


class CancelOrderAPI(Resource):
    """API to cancel an order

    ...

    Methods
    -------
    post():
        Handle Cancel Order API POST request from the client
    """

    def post(self) -> Tuple[dict, int]:
        """Handle Cancel Order API POST request from the client

        ...

        Parameters
        ----------
        None

        Returns
        -------
        `response` (Tuple[dict, int]):

            In case of successfully: Include a `message` response string and HTTP `status_code` 200.
            - `message` (string):
                A message state that operation is successfully executed.
            - `modified_date` (string):
                Datetime that action is success
            - `status_code` (int):
                Successful code: 200

            In case of failed: Include a `failed` response dictionary and HTTP `status_code` 400.
            - `failed` (dict):
                Include `message`  and `error` - error details.
            - `status_code` (int):
                Fails code: 400
        """

        try:
            print("Cancel order called")
            raw_data = request.get_json(force=True)

            order_id = Validator.validate_order_cancel_request(
                raw_data=raw_data)
            print("order id : ",order_id)
            modified_date = OrderService.cancel_order_service(order_id=order_id)
        except Exception as e:
            return {
                "message": "Failed to set order status to canceled",
                "error": str(e)
            }, 400

        return {
            "message": "Cancel order successfully",
            "modified_date": modified_date
        }, 200


class RefundOrderAPI(Resource):
    """API to refund an order

    ...

    Methods
    -------
    post():
        Handle Refund Order API POST request from the client
    """

    def post(self) -> Tuple[dict, int]:
        """Handle Refund Order API POST request from the client

        ...

        Parameters
        ----------
        None

        Returns
        -------
        `response` (Tuple[dict, int]):

            In case of successfully: Include a `message` response string and HTTP `status_code` 200.
            - `message` (string):
                A message state that operation is successfully executed.
            - `modified_date` (string):
                Datetime that action is success
            - `order_id` (int):
                The id of the modified order
            - `status_code` (int):
                Successful code: 200

            In case of failed: Include a `failed` response dictionary and HTTP `status_code` 400.
            - `failed` (dict):
                Include `message`  and `error` - error details.
            - `status_code` (int):
                Fails code: 400
        """

        try:
            raw_data = request.get_json(force=True)
            raw_data["system_pincode"] = current_app.config["PINCODE"]

            order_id = Validator.validate_order_refund_request(
                raw_data=raw_data)

            # Return the modified date and order_id of the refunded order.
            modified_date = OrderService.refund_order_service(order_id=order_id)
        except Exception as e:
            return {
                "message": "Failed to set order status to refunded",
                "error": str(e)
            }, 400

        return {
            "message": "Refund order successfully",
            "modified_date": modified_date,
            "order_id": order_id,
        }, 200


class CancelItemAPI(Resource):
    """API to cancel an order's item

    ...

    Methods
    -------
    post():
        Handle Cancel Item API POST request from the client
    """

    def post(self) -> Tuple[dict, int]:
        """Handle Cancel Item API POST request from the client

        ...

        Parameters
        ----------
        None

        Returns
        -------
        `response` (Tuple[dict, int]):

            In case of successfully: Include a `message` response string and HTTP `status_code` 200.
            Also, this API will send a socket request to the frontend to update.
            - `message` (string):
                A message state that operation is successfully executed.
            - `item_id` (int):
                ID of the affected item.
            - `status_code` (int):
                Successful code: 200

            In case of failed: Include a `failed` response dictionary and HTTP `status_code` 400.
            - `failed` (dict):
                Include `message`  and `error` - error details.
            - `status_code` (int):
                Fails code: 400
        """

        try:
            raw_data = request.get_json(force=True)

            # Returning the new status and the affected item id
            item_id = raw_data["item_id"]

            # Get the item status after cancel.
            item_status = ItemService.cancel_item_service(item_id=item_id)
        except Exception as e:
            return {
                "message": "Failed to set item status to canceled",
                "error": str(e)
            }, 400

        return {
            "message": "Cancel item successfully",
            "item_status": item_status,
            "item_id": item_id,
        }, 200


class FinishItemAPI(Resource):
    """API to finish an order's item

    ...

    Methods
    -------
    post():
        Handle Finish Item API POST request from the client
    """

    def post(self) -> Tuple[dict, int]:
        """Handle Finish Item API POST request from the client

        ...

        Parameters
        ----------
        None

        Returns
        -------
        `response` (Tuple[dict, int]):

            In case of successfully: Include a `message` response string and HTTP `status_code` 200.
            Also, this API will send a socket request to the frontend to update.
            - `message` (string):
                A message state that operation is successfully executed.
            - `item_id` (int):
                ID of the affected item.
            - `status_code` (int):
                Successful code: 200

            In case of failed: Include a `failed` response dictionary and HTTP `status_code` 400.
            - `failed` (dict):
                Include `message`  and `error` - error details.
            - `status_code` (int):
                Fails code: 400
        """

        try:
            raw_data = request.get_json(force=True)

            # Returning the new status and the affected item id
            item_id = raw_data["item_id"]
            item_status = ItemService.finish_item_service(item_id=item_id)
        except Exception as e:
            return {
                "message": "Failed to set item status to finish",
                "error": str(e)
            }, 400

        return {
            "message": "Finish item successfully",
            "item_status": item_status,
            "item_id": item_id,
        }, 200


class ParkBottleAPI(Resource):
    """API to park a bottle

    ...

    Methods
    -------
    post():
        Handle Bottle Parking API POST request from the client
    """

    def post(self) -> Tuple[dict, int]:
        """Handle Bottle Parking API POST request from the client

        ...

        Parameters
        ----------
        None

        Returns
        -------
        `response` (Tuple[dict, int]):

            In case of successfully: Include a `message` response string and HTTP `status_code` 200.
            Also, this API will send a socket request to the frontend to update.
            - `message` (string):
                A message state that operation is successfully executed.
            - `status_code` (int):
                Successful code: 200

            In case of failed: Include a `failed` response dictionary and HTTP `status_code` 400.
            - `failed` (dict):
                Include `message`  and `error` - error details.
            - `status_code` (int):
                Fails code: 400
        """

        try:
            raw_data = request.get_json(force=True)

        except Exception as e:
            return {
                "message": "Failed to park a bottle",
                "error": str(e)
            }, 400

        return {
            "message": "Park a bottle successfully",
        }, 200

class InsertUserActionsAPI(Resource):
    def post(self) -> Tuple[dict,int]:
        try:
            raw_data = request.get_json(force=True)
            order_id = OrderService.insert_order_actions(raw_data)
        except Exception as e:
            return {
                "message": "Failed to get data",
                "error": str(e)
            }, 400

        return {
            "message": "Actions received  ",
            "order_id": order_id
        }, 200
