from app.utils import OrderUtils
from app.api_config import APIConfig


def test_update_order_item_finish_success(app, client):
    """Test if we can mark an item as "done"
    if the order is in_progress.
    """
    with app.app_context():
        from app.query import get_order_items, insert_order

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
                {
                    "name": "Cinnamon",
                    "quantity": 1,
                    "price": .5
                },
                {
                    "name": "Olympic",
                    "quantity": 3,
                    "price": 1.5
                },
            ],
            "user_id": None,
            "user_point": None,
            "time_spent": "58",
        }

        order_id = insert_order(data=data)

        item_id_list = [item["id"] for item in get_order_items(order_id=order_id)]

        # Try marking all items as done.
        for item_id in item_id_list:
            response = client.post(APIConfig.get_testing_endpoint("FINISH_ITEM_API"), json={
                "item_id": item_id
            })

            assert response.status_code == 200

        # Double-check if the item status is updated.
        checking_item_list = get_order_items(order_id=order_id)

        for item in checking_item_list:
            assert item["status"] == OrderUtils.FINISHED_ITEM_STATUS


def test_update_order_item_finish_failed_crazy_item_id(client):
    """Test if we failed to send a request with a crazy item_id"""

    response = client.post(APIConfig.get_testing_endpoint("FINISH_ITEM_API"), json={
        "item_id": "Daniolo Zaniolo"
    })

    assert response.status_code == 400


def test_update_order_item_finish_failed_not_exist_item_id(client):
    """Test if we failed to send a request with a not-exist item_id"""

    response = client.post(APIConfig.get_testing_endpoint("FINISH_ITEM_API"), json={
        "item_id": 19969991
    })

    assert response.status_code == 400


def test_update_order_item_finish_failed_finished_order(app, client):
    """Test if we can't mark an item as "canceled"
    if the order is finished.
    """
    with app.app_context():
        from app.query import finish_order, get_order_items, insert_order

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
                {
                    "name": "Cinnamon",
                    "quantity": 1,
                    "price": .5
                },
                {
                    "name": "Olympic",
                    "quantity": 3,
                    "price": 1.5
                },
            ],
            "user_id": None,
            "user_point": None,
            "time_spent": "58",
        }

        order_id = insert_order(data=data)
        _ = finish_order(order_id=order_id)

        item_id_list = [item["id"] for item in get_order_items(order_id=order_id)]

        # Try marking all items as canceled.
        for item_id in item_id_list:
            response = client.post(APIConfig.get_testing_endpoint("CANCEL_ITEM_API"), json={
                "item_id": item_id
            })

            assert response.status_code == 400

        # Double-check if the item status is updated.
        checking_item_list = get_order_items(order_id=order_id)

        for item in checking_item_list:
            assert item["status"] == OrderUtils.FINISHED_ITEM_STATUS


def test_update_order_item_finish_failed_canceled_order(app, client):
    """Test if we can't mark an item as "done"
    if the order is finished.
    """
    with app.app_context():
        from app.query import cancel_order, get_order_items, insert_order

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
                {
                    "name": "Cinnamon",
                    "quantity": 1,
                    "price": .5
                },
                {
                    "name": "Olympic",
                    "quantity": 3,
                    "price": 1.5
                },
            ],
            "user_id": None,
            "user_point": None,
            "time_spent": "58",
        }

        order_id = insert_order(data=data)
        _ = cancel_order(order_id=order_id)

        item_id_list = [item["id"] for item in get_order_items(order_id=order_id)]

        # Try marking all items as done.
        for item_id in item_id_list:
            response = client.post(APIConfig.get_testing_endpoint("FINISH_ITEM_API"), json={
                "item_id": item_id
            })

            assert response.status_code == 400

        # Double-check if the item status is updated.
        checking_item_list = get_order_items(order_id=order_id)

        for item in checking_item_list:
            assert item["status"] == OrderUtils.CANCELED_ITEM_STATUS


def test_update_order_item_finish_failed_refunded_order(app, client):
    """Test if we can't mark an item as "canceled"
    if the order is refunded.
    """
    with app.app_context():
        from app.query import (finish_order, get_order_items, insert_order,
                               refund_order)

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
                {
                    "name": "Cinnamon",
                    "quantity": 1,
                    "price": .5
                },
                {
                    "name": "Olympic",
                    "quantity": 3,
                    "price": 1.5
                },
            ],
            "user_id": None,
            "user_point": None,
            "time_spent": "58",
        }

        order_id = insert_order(data=data)

        # Finish and then refund that order
        _ = finish_order(order_id=order_id)
        _ = refund_order(order_id=order_id)

        item_id_list = [item["id"] for item in get_order_items(order_id=order_id)]

        # Try marking all items as canceled.
        for item_id in item_id_list:
            response = client.post(APIConfig.get_testing_endpoint("CANCEL_ITEM_API"), json={
                "item_id": item_id
            })

            assert response.status_code == 400

        # Double-check if the item status is updated.
        checking_item_list = get_order_items(order_id=order_id)

        for item in checking_item_list:
            assert item["status"] == OrderUtils.FINISHED_ITEM_STATUS


def test_update_order_item_cancel_success(app, client):
    """Test if we can mark an item as "canceled"
    if the order is in_progress.
    """
    with app.app_context():
        from app.query import get_order_items, insert_order

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
                {
                    "name": "Cinnamon",
                    "quantity": 1,
                    "price": .5
                },
                {
                    "name": "Olympic",
                    "quantity": 3,
                    "price": 1.5
                },
            ],
            "user_id": None,
            "user_point": None,
            "time_spent": "58",
        }

        order_id = insert_order(data=data)

        item_id_list = [item["id"] for item in get_order_items(order_id=order_id)]

        # Try marking all items as done.
        for item_id in item_id_list:
            response = client.post(APIConfig.get_testing_endpoint("CANCEL_ITEM_API"), json={
                "item_id": item_id
            })

            assert response.status_code == 200

        # Double-check if the item status is updated.
        checking_item_list = get_order_items(order_id=order_id)

        for item in checking_item_list:
            assert item["status"] == OrderUtils.CANCELED_ITEM_STATUS


def test_update_order_item_cancel_failed_crazy_item_id(client):
    """Test if we failed to send a request with a crazy item_id"""

    response = client.post(APIConfig.get_testing_endpoint("CANCEL_ITEM_API"), json={
        "item_id": "Daniolo Zaniolo"
    })

    assert response.status_code == 400


def test_update_order_item_cancel_failed_not_exist_item_id(client):
    """Test if we failed to send a request with a non-exist item_id"""

    response = client.post(APIConfig.get_testing_endpoint("CANCEL_ITEM_API"), json={
        "item_id": 19969991
    })

    assert response.status_code == 400


def test_update_order_preserve_item_status(app, client):
    """Test if the item status is preserved when an order is marked as done."""

    with app.app_context():
        from app.query import finish_order, get_order_items, insert_order

        # Dummy test data
        data = {
            "order_table": 1,
            "order_type": "dine_in",
            "order_items": [
                {
                    "name": "Titanic",
                    "quantity": 1,
                    "price": .5
                },
                {
                    "name": "Cinnamon",
                    "quantity": 1,
                    "price": .5
                }
            ],
            "user_id": None,
            "user_point": None,
            "time_spent": "58",
        }

        order_id = insert_order(data=data)

        item_id_list = [item["id"] for item in get_order_items(order_id=order_id)]

        # Finish the first and cancel the second item
        _ = client.post(APIConfig.get_testing_endpoint("FINISH_ITEM_API"), json={
            "item_id": item_id_list[0]
        })
        _ = client.post(APIConfig.get_testing_endpoint("CANCEL_ITEM_API"), json={
            "item_id": item_id_list[1]
        })

        # Finish that order
        _ = finish_order(order_id=order_id)

        confirm_item_list = get_order_items(order_id=order_id)

        # Now make sure that the first order item has the status of 1,
        # while the other order item still has the status of 2.
        for item in confirm_item_list:
            if item["id"] == item_id_list[0]:
                assert item["status"] == OrderUtils.FINISHED_ITEM_STATUS
            if item["id"] == item_id_list[1]:
                assert item["status"] == OrderUtils.CANCELED_ITEM_STATUS
