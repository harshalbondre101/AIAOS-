from app.utils import OrderUtils
from app.api_config import APIConfig


def test_cancel_order_success(app, client):
    """Test if the order cancel API works well
    with valid data
    """

    with app.app_context():
        from app.query import get_or_create_user, get_order, insert_order

        # Get a random user
        user_id = get_or_create_user(phone_number="20010")

        # Create a dummy order
        data = {
            "order_table": 1,
            "order_type": "dine_in",
            "order_items": [
                {
                    "name": "Titanic",
                    "quantity": 1,
                    "price": .5
                },
            ],
            "user_id": user_id["id"],
            "user_point": 20,
            "time_spent": "58",
        }

        order_id = insert_order(data=data)

        # Try cancel that order
        response = client.post(APIConfig.get_testing_endpoint("CANCEL_ORDER_API"), json={
            "order_id": order_id
        })

        # Then get the information from the database and asssertion
        order_detail = get_order(order_id=order_id)

        assert response.status_code == 200

        # The order must be marked as "canceled"
        assert order_detail["order_status"] == "2"

        # All items must be marked as "canceled"
        for item in order_detail["order_items"]:
            assert item["item_status"] == "2"


def test_cancel_order_failed_empty_order_id(app, client):
    """Test if the order cancel API throws an error
    with empty order_id
    """

    with app.app_context():
        # Try cancel with empty order_id
        response = client.post(APIConfig.get_testing_endpoint("CANCEL_ORDER_API"), json={
            "order_id": ""
        })

        assert response.status_code == 400
        assert "order_id" in response.json["error"]


def test_cancel_order_failed_crazy_order_id(app, client):
    """Test if the order cancel API throws an error
    with empty order_id
    """

    with app.app_context():
        # Try cancel with crazy order_id
        response = client.post(APIConfig.get_testing_endpoint("FINISH_ORDER_API"), json={
            "order_id": "Daniolo Zaniolo"
        })

        assert response.status_code == 400
        assert "order_id" in response.json["error"]


def test_cancel_order_failed_order_id_not_exist(app, client):
    """Test if we can't cancel a non-exist order
    """

    with app.app_context():
        # Try cancel with non-exist order_id
        response = client.post(APIConfig.get_testing_endpoint("FINISH_ORDER_API"), json={
            "order_id": "13377331"
        })

        assert response.status_code == 400
        assert "order_id" in response.json["error"]


def test_finish_order_failed_change_status_a_canceled_order(app, client):
    """Test if we can't change a canceled order status to finished.
    """

    with app.app_context():
        from app.query import (cancel_order, get_or_create_user, get_order,
                               insert_order)

        # Get a random user
        user_id = get_or_create_user(phone_number="20010")

        # Create a dummy order & finish it
        data = {
            "order_table": 1,
            "order_type": "dine_in",
            "order_items": [
                {
                    "name": "Titanic",
                    "quantity": 1,
                    "price": .5
                },
            ],
            "user_id": user_id["id"],
            "user_point": 20,
            "time_spent": "58",
        }

        order_id = insert_order(data=data)

        _ = cancel_order(order_id=order_id)

        # Try posting a cancel status to it
        finish_endpoint_response = client.post(APIConfig.get_testing_endpoint("FINISH_ORDER_API"), json={
            "order_id": order_id
        })

        order_detail_after_post = get_order(order_id=order_id)

        assert finish_endpoint_response.status_code == 400
        assert "order_id" in finish_endpoint_response.json["error"]
        assert order_detail_after_post["order_status"] == "2"

        for item in order_detail_after_post["order_items"]:
            assert item["item_status"] == "2"


def test_finish_order_success(app, client):
    """Test if the order finish API works well
    with valid data
    """

    phone_number = "20010"

    with app.app_context():
        from app.query import get_or_create_user, get_order, insert_order

        # Get a random user
        user_id = get_or_create_user(phone_number=phone_number)

        # Create a dummy order
        data = {
            "order_table": 1,
            "order_type": "dine_in",
            "order_items": [
                {
                    "name": "Titanic",
                    "quantity": 1,
                    "price": .5
                },
            ],
            "user_id": user_id["id"],
            "user_point": 69,
            "time_spent": "58",
        }

        order_id = insert_order(data=data)

        # Try cancel that order
        response = client.post(APIConfig.get_testing_endpoint("FINISH_ORDER_API"), json={
            "order_id": order_id
        })

        # Then get the information from the database and asssertion
        order_detail = get_order(order_id=order_id)
        user_detail = get_or_create_user(phone_number=phone_number)

        assert response.status_code == 200

        # The order must be marked as finished
        assert order_detail["order_status"] == OrderUtils.FINISHED_ORDER_STATUS

        # By default (no item marked canceled),
        # all items should be marked as "finished".
        for item in order_detail["order_items"]:
            assert item["item_status"] == OrderUtils.FINISHED_ITEM_STATUS

        # Make sure the points are updated.
        assert user_detail["points"] == data["user_point"]


def test_finish_order_failed_empty_order_id(app, client):
    """Test if the order finish API throws an error
    with empty order_id
    """

    with app.app_context():
        # Try finish with empty order_id
        response = client.post(APIConfig.get_testing_endpoint("FINISH_ORDER_API"), json={
            "order_id": ""
        })

        assert response.status_code == 400
        assert "order_id" in response.json["error"]


def test_finish_order_failed_crazy_order_id(app, client):
    """Test if the order finish API throws an error
    with crazy order_id
    """

    with app.app_context():
        # Try finish with crazy order_id
        response = client.post(APIConfig.get_testing_endpoint("FINISH_ORDER_API"), json={
            "order_id": "Daniolo Zaniolo"
        })

        assert response.status_code == 400
        assert "order_id" in response.json["error"]


def test_finish_order_failed_order_id_not_exist(app, client):
    """Test if we can't finish a non-exist order
    """

    with app.app_context():
        # Try finish with non-exist order_id
        response = client.post(APIConfig.get_testing_endpoint("FINISH_ORDER_API"), json={
            "order_id": "13377331"
        })

        assert response.status_code == 400
        assert "order_id" in response.json["error"]


def test_finish_order_failed_change_status_a_finished_order(app, client):
    """Test if we can't change status a finished order to canceled.
    """

    with app.app_context():
        from app.query import (finish_order, get_or_create_user, get_order,
                               insert_order)

        # Get a random user
        user_id = get_or_create_user(phone_number="20010")

        # Create a dummy order & finish it
        data = {
            "order_table": 1,
            "order_type": "dine_in",
            "order_items": [
                {
                    "name": "Titanic",
                    "quantity": 1,
                    "price": .5
                },
            ],
            "user_id": user_id["id"],
            "user_point": 20,
            "time_spent": "58",
        }

        order_id = insert_order(data=data)

        _ = finish_order(order_id=order_id)

        # Try posting a cancel status to it
        cancel_endpoint_response = client.post(APIConfig.get_testing_endpoint("CANCEL_ORDER_API"), json={
            "order_id": order_id
        })

        order_detail_after_post = get_order(order_id=order_id)

        assert cancel_endpoint_response.status_code == 400
        assert "order_id" in cancel_endpoint_response.json["error"]
        assert order_detail_after_post["order_status"] == "1"

        for item in order_detail_after_post["order_items"]:
            assert item["item_status"] == "1"


def test_refund_finish_order_success(app, client):
    """Test if the order refund API works well
    with valid data
    """

    with app.app_context():
        from app.query import get_or_create_user, get_order, insert_order, finish_order

        # Get a random user
        user_id = get_or_create_user(phone_number="20010")

        # Create a dummy order
        data = {
            "order_table": 1,
            "order_type": "dine_in",
            "order_items": [
                {
                    "name": "Titanic",
                    "quantity": 1,
                    "price": .5
                },
            ],
            "user_id": user_id["id"],
            "user_point": 20,
            "time_spent": "58",
        }

        order_id = insert_order(data=data)

        # Finish it
        _ = finish_order(order_id=order_id)

        # Try refund that order
        response = client.post(APIConfig.get_testing_endpoint("REFUND_ORDER_API"), json={
            "order_id": order_id,
            "pincode": "131337"
        })

        # Then get the information from the database and asssertion
        order_detail = get_order(order_id=order_id)

        assert response.status_code == 200

        # The order must be marked as refunded
        assert order_detail["order_status"] == OrderUtils.REFUNDED_ORDER_STATUS


def test_refund_finish_order_failed_wrong_pincode(app, client):
    """Test if the order refund API fails
    with wrong pincode
    """

    with app.app_context():
        from app.query import get_or_create_user, get_order, insert_order, finish_order

        # Get a random user
        user_id = get_or_create_user(phone_number="20010")

        # Create a dummy order
        data = {
            "order_table": 1,
            "order_type": "dine_in",
            "order_items": [
                {
                    "name": "Titanic",
                    "quantity": 1,
                    "price": .5
                },
            ],
            "user_id": user_id["id"],
            "user_point": 20,
            "time_spent": "58",
        }

        order_id = insert_order(data=data)

        # Finish it
        _ = finish_order(order_id=order_id)

        # Try refund that order
        response = client.post(APIConfig.get_testing_endpoint("REFUND_ORDER_API"), json={
            "order_id": order_id,
            "pincode": "696969"
        })

        # Then get the information from the database and asssertion
        order_detail = get_order(order_id=order_id)

        assert response.status_code == 400

        # The order still not be mark as refunded
        assert order_detail["order_status"] != OrderUtils.REFUNDED_ORDER_STATUS
        assert "pincode" in response.json["error"]


def test_refund_finish_order_failed_crazy_order_id(client):
    """Test if the order refund API failed
    with crazy order_id
    """

    # Try refund that order
    response = client.post(APIConfig.get_testing_endpoint("REFUND_ORDER_API"), json={
        "order_id": "Daniolo Zaniolo",
        "pincode": "131337"
    })

    assert response.status_code == 400
    assert "order_id" in response.json["error"]


def test_refund_finish_order_failed_order_id_not_exist(client):
    """Test if the order refund API fails
    with order_id not exist
    """

    # Try refund that order
    response = client.post(APIConfig.get_testing_endpoint("REFUND_ORDER_API"), json={
        "order_id": 9999,
        "pincode": "131337"
    })

    assert response.status_code == 400
    assert "order_id" in response.json["error"]


def test_refund_finish_order_failed_order_canceled(app, client):
    """Test if the order refund API fails
    with canceled order
    """

    with app.app_context():
        from app.query import get_or_create_user, get_order, insert_order, cancel_order

        # Get a random user
        user_id = get_or_create_user(phone_number="20010")

        # Create a dummy order
        data = {
            "order_table": 1,
            "order_type": "dine_in",
            "order_items": [
                {
                    "name": "Titanic",
                    "quantity": 1,
                    "price": .5
                },
            ],
            "user_id": user_id["id"],
            "user_point": 20,
            "time_spent": "58",
        }

        order_id = insert_order(data=data)

        # Finish it
        _ = cancel_order(order_id=order_id)

        # Try refund that order
        response = client.post(APIConfig.get_testing_endpoint("REFUND_ORDER_API"), json={
            "order_id": order_id,
            "pincode": "131337"
        })

        # Then get the information from the database and asssertion
        order_detail = get_order(order_id=order_id)

        assert response.status_code == 400

        # The order must be marked as refunded
        assert order_detail["order_status"] == OrderUtils.CANCELED_ORDER_STATUS
        assert "order_id" in response.json["error"]


def test_refund_finish_order_failed_order_in_progress(app, client):
    """Test if the order refund API fails
    with order in_progress
    """

    with app.app_context():
        from app.query import get_or_create_user, get_order, insert_order, cancel_order

        # Get a random user
        user_id = get_or_create_user(phone_number="20010")

        # Create a dummy order
        data = {
            "order_table": 1,
            "order_type": "dine_in",
            "order_items": [
                {
                    "name": "Titanic",
                    "quantity": 1,
                    "price": .5
                },
            ],
            "user_id": user_id["id"],
            "user_point": 20,
            "time_spent": "58",
        }

        order_id = insert_order(data=data)

        # Try refund that order
        response = client.post(APIConfig.get_testing_endpoint("REFUND_ORDER_API"), json={
            "order_id": order_id,
            "pincode": "131337"
        })

        # Then get the information from the database and asssertion
        order_detail = get_order(order_id=order_id)

        assert response.status_code == 400

        # The order must be marked as refunded
        assert order_detail["order_status"] == '0'
        assert "order_id" in response.json["error"]
