# Defining testing endpoints
import time

from app.api_config import APIConfig


def test_get_username_list_success(client):
    """Test if the API is working, can generate 10 names"""
    response = client.get(APIConfig.get_testing_endpoint("GET_USER_NAME_API"), json={
        "max_results": 10
    })
    assert response.status_code == 200
    assert len(response.json["name_list"]) == 10


def test_get_username_list_failed_crazy_max_results(client):
    """Test if the API fails when max_results is crazy"""
    response = client.get(APIConfig.get_testing_endpoint("GET_USER_NAME_API"), json={
        "max_results": "Daniolo Zaniolo"
    })
    assert response.status_code == 400
    assert "max_results" in response.json["error"]


def test_get_username_list_failed_zero_max_results(client):
    """Test if the API fails when max_results is zero"""
    response = client.get(APIConfig.get_testing_endpoint("GET_USER_NAME_API"), json={
        "max_results": 0
    })
    assert response.status_code == 400
    assert "max_results" in response.json["error"]


def test_create_new_user(app, client):
    """Test if the API is working, can store a new client"""

    with app.app_context():
        from app.query import finish_order, insert_order

        # Insert new order to guarantee there are items to recommend
        order_data = {
            "order_table": 1,
            "order_type": "dine_in",
            "order_items": [
                {
                    "name": "London",
                    "quantity": 10,
                    "price": 22.5  # 225
                },
                {
                    "name": "Paris",
                    "quantity": 30,
                    "price": 10  # 300
                },
                {
                    "name": "Moscow",
                    "quantity": 20,
                    "price": 10.5  # 210
                },
                {
                    "name": "New York",
                    "quantity": 30,
                    "price": 10.5  # 315
                },
                {
                    "name": "Berlin",
                    "quantity": 50,
                    "price": 26.5  # 1325
                }
            ],
            "user_id": None,
            "user_point": None,
            "time_spent": "58"
        }

        order_id = insert_order(data=order_data)
        _ = finish_order(order_id=order_id)

        # Create a new user
        phone_number = "69696"

        data = {
            "phone_number": phone_number
        }

        response = client.post(APIConfig.get_testing_endpoint("GET_USER_API"), json=data)
        assert response.status_code == 200
        assert response.json["user"]["points"] == 0
        assert response.json["user"]["name"] is None

        # The server will return a list of best seller items.
        assert len(response.json["latest_items"]) == 5
        assert response.json["latest_items"] == [
            {"name": "Berlin", "price": 26.5},
            {"name": "New York", "price": 10.5},
            {"name": "Paris", "price": 10},
            {"name": "London", "price": 22.5},
            {"name": "Moscow", "price": 10.5},
        ]


def test_get_existed_user(app, client):
    """Test if an existed user info will be returned, rather than creating a new one."""
    with app.app_context():
        from app.query import get_or_create_user

        phone_number = "99999"

        data = {
            "phone_number": phone_number
        }

        # Create that user
        existing_user = get_or_create_user(phone_number=phone_number)

        # Then try use the API to call, again
        response = client.post(APIConfig.get_testing_endpoint("GET_USER_API"), json=data)
        assert response.status_code == 200
        assert response.json["user"]["id"] == existing_user["id"]
        assert response.json["user"]["name"] is None


def test_get_existed_user_with_recent_orders(app, client):
    """Test if an existed user info will be returned, with latest order list."""

    phone_number = "99699"

    with app.app_context():
        from app.query import finish_order, get_or_create_user, insert_order

        user_id = get_or_create_user(phone_number=phone_number)

        # Data of each order
        data1 = {
            "order_table": 3,
            "order_type": "dine_in",
            "order_items": [
                {
                    "name": "Marseille",
                    "quantity": 1,
                    "price": .5
                },
                {
                    "name": "Grenoble",
                    "quantity": 1,
                    "price": .5
                },
                # Gift
                {
                    "name": "Lyon",
                    "quantity": 1,
                    "price": 0
                },
            ],
            "user_id": user_id["id"],
            "user_point": 20,
            "time_spent": "58",
        }

        data2 = {
            "order_table": 3,
            "order_type": "dine_in",
            "order_items": [
                {
                    "name": "Titanic",
                    "quantity": 1,
                    "price": 1.5
                },
                {
                    "name": "Catalan",
                    "quantity": 1,
                    "price": 2.5
                },
                # Gift
                {
                    "name": "Olympic",
                    "quantity": 1,
                    "price": 0
                },
            ],
            "user_id": user_id["id"],
            "user_point": 50,
            "time_spent": "58",
        }

        # Insert and finish these 2 orders
        order_id_1 = insert_order(data=data1)
        _ = finish_order(order_id=order_id_1)

        # Sleep 2 seconds to create the difference in time.
        time.sleep(2)

        order_id_2 = insert_order(data=data2)
        _ = finish_order(order_id=order_id_2)

        # Test if return information got the latest i.e. the 2nd order items
        response = client.post(APIConfig.get_testing_endpoint("GET_USER_API"), json={
            "phone_number": phone_number
        })

        assert response.status_code == 200
        assert response.json["user"]["points"] == 50.0
        assert response.json["latest_items"] == [
            {
                "name": "Catalan",
                "price": 2.5
            },
            {
                "name": "Titanic",
                "price": 1.5
            },
            {
                "name": "Olympic",
                "price": 0
            }
        ]


def test_get_crazy_user(client):
    """Test if a crazy phone cannot be created."""

    phone_number = "anhquanvippro"

    data = {
        "phone_number": phone_number
    }

    # Then try use the API to call, again
    response = client.post(APIConfig.get_testing_endpoint("GET_USER_API"), json=data)
    assert response.status_code == 400
    assert "phone_number" in response.json["error"]


def test_change_name_success(app, client):
    """Test if the API is working, can change the user's name"""
    phone_number = "13133"

    with app.app_context():
        from app.query import get_or_create_user
        user = get_or_create_user(phone_number=phone_number)

        name = "Daniolo"

        response = client.post(APIConfig.get_testing_endpoint("UPDATE_USER_NAME_API"), json={
            "user_id": user["id"],
            "user_name": name
        })

        checking_user = get_or_create_user(phone_number=phone_number)

        assert response.status_code == 200
        assert checking_user["name"] == name


def test_change_name_failed_empty_name(app, client):
    """Test if the API is failed when name is empty"""
    phone_number = "13133"

    with app.app_context():
        from app.query import get_or_create_user
        user = get_or_create_user(phone_number=phone_number)

        response = client.post(APIConfig.get_testing_endpoint("UPDATE_USER_NAME_API"), json={
            "user_id": user["id"],
            "user_name": ""
        })

        assert response.status_code == 400
        assert "user_name" in response.json["error"]


def test_change_name_failed_id_not_exists(app, client):
    """Test if the API is failed when id is crazy"""
    response = client.post(APIConfig.get_testing_endpoint("UPDATE_USER_NAME_API"), json={
        "user_id": 99999,
        "user_name": "Daniolo"
    })

    assert response.status_code == 400
    assert "user_id" in response.json["error"]
