from app.api_config import APIConfig


def test_creating_order_dine_in_with_exist_user_success(app, client):
    """Test if we can create a new dine_in order successfully
    with valid informations
    """

    with app.app_context():
        from app.query import get_or_create_user, get_order

        user_id = get_or_create_user(phone_number="12345")

        data = {
            "order_table": 1,
            "user": {
                "id": user_id["id"],
                "points": 20
            },
            "order_type": "dine_in",
            "order_items": [
                {
                    "name": "Titanic",
                    "quantity": 1,
                    "price": 0.5
                },
                {
                    "name": "Olympic",
                    "quantity": 1,
                    "price": 1.5
                }
            ],
            "time_spent": "58"
        }

        response = client.post(APIConfig.get_testing_endpoint("CREATE_ORDER_API"), json=data)
        assert response.status_code == 200

        # Make sure there are a user record in this.
        new_order = get_order(order_id=response.json["new_order_id"])
        assert new_order["user_id"] == data["user"]["id"]
        assert new_order["user_point"] == data["user"]["points"]


def test_creating_order_take_away_with_exist_user_success(app, client):
    """Test if we can create a new take_away order successfully
    with valid informations
    """
    with app.app_context():
        from app.query import get_or_create_user

        user_id = get_or_create_user(phone_number="12345")

        data = {
            "order_table": 1,
            "user": {
                "id": user_id["id"],
                "points": 20
            },
            "order_type": "take_away",
            "order_items": [
                {
                    "name": "Titanic",
                    "quantity": 1,
                    "price": 0.5
                },
                {
                    "name": "Olympic",
                    "quantity": 1,
                    "price": 1.5
                }
            ],
            "time_spent": "58"
        }

        response = client.post(APIConfig.get_testing_endpoint("CREATE_ORDER_API"), json=data)
        assert response.status_code == 200


def test_creating_order_dine_in_with_no_user_success(app, client):
    """Test if we can create a new dine_in order successfully
    with valid informations
    """

    with app.app_context():
        from app.query import get_order

        data = {
            "order_table": 1,
            "order_type": "take_away",
            "order_items": [
                {
                    "name": "Titanic",
                    "quantity": 1,
                    "price": .5
                },
                {
                    "name": "Olympic",
                    "quantity": 1,
                    "price": 1.5
                }
            ],
            "time_spent": "58"
        }

        response = client.post(APIConfig.get_testing_endpoint("CREATE_ORDER_API"), json=data)
        assert response.status_code == 200

        # Assert that the order has no user or point attached.
        new_order_id = response.json["new_order_id"]
        order_detail = get_order(order_id=new_order_id)
        assert order_detail["user_id"] is None
        assert order_detail["user_point"] is None


def test_creating_order_take_away_with_no_user_success(app, client):
    """Test if we can create a new take_away order successfully
    with valid informations
    """

    with app.app_context():
        from app.query import get_order

        data = {
            "order_table": 1,
            "order_type": "take_away",
            "order_items": [
                {
                    "name": "Titanic",
                    "quantity": 1,
                    "price": .5
                },
                {
                    "name": "Olympic",
                    "quantity": 1,
                    "price": 1.5
                }
            ],
            "time_spent": "58"
        }

        response = client.post(APIConfig.get_testing_endpoint("CREATE_ORDER_API"), json=data)
        assert response.status_code == 200

        # Assert that the order has no user or point attached.
        new_order_id = response.json["new_order_id"]
        order_detail = get_order(order_id=new_order_id)
        assert order_detail["user_id"] is None
        assert order_detail["user_point"] is None


def test_creating_order_failed_missing_table(app, client):
    """Test if we can create a new order unsuccessfully
    with informations missing order_table
    """

    with app.app_context():
        from app.query import get_or_create_user

        user_id = get_or_create_user(phone_number="12345")

        data = {
            "order_type": "dine_in",
            "user": {
                "id": user_id["id"],
                "points": 20
            },
            "order_items": [
                {
                    "name": "Titanic",
                    "quantity": 1,
                    "price": .5
                },
                {
                    "name": "Olympic",
                    "quantity": 1,
                    "price": 1.5
                }
            ],
            "time_spent": "58"
        }

        response = client.post(APIConfig.get_testing_endpoint("CREATE_ORDER_API"), json=data)
        assert response.status_code == 400
        assert "order_table" in response.json["error"]


def test_creating_order_failed_dine_in_crazy_table(app, client):
    """Test if we can create a new order unsuccessfully
    with a crazy order_table
    """

    with app.app_context():
        from app.query import get_or_create_user

        user_id = get_or_create_user(phone_number="12345")

        data = {
            "order_type": "dine_in",
            "order_table": "Daniolo Zaniolo",
            "user": {
                "id": user_id["id"],
                "points": 20
            },
            "order_items": [
                {
                    "name": "Titanic",
                    "quantity": 1,
                    "price": .5
                },
                {
                    "name": "Olympic",
                    "quantity": 1,
                    "price": 1.5
                }
            ],
            "time_spent": "58"
        }

        response = client.post(APIConfig.get_testing_endpoint("CREATE_ORDER_API"), json=data)
        assert response.status_code == 400
        assert "order_table" in response.json["error"]


def test_creating_order_failed_dine_in_out_of_range_table(app, client):
    """Test if we can create a new order unsuccessfully
    with order_table is some strange table (maybe not exist in range).
    """

    with app.app_context():
        from app.query import get_or_create_user

        user_id = get_or_create_user(phone_number="12345")

        data = {
            "order_type": "dine_in",
            "order_table": 99999,
            "user": {
                "id": user_id["id"],
                "points": 20
            },
            "order_items": [
                {
                    "name": "Titanic",
                    "quantity": 1,
                    "price": .5
                },
                {
                    "name": "Olympic",
                    "quantity": 1,
                    "price": 1.5
                }
            ],
            "time_spent": "58"
        }

        # Out of range (larger than the upper bound)
        response = client.post(APIConfig.get_testing_endpoint("CREATE_ORDER_API"), json=data)
        assert response.status_code == 400
        assert "order_table" in response.json["error"]

        # Out of range (smaller than the lower bound)
        data["order_table"] = 0
        response = client.post(APIConfig.get_testing_endpoint("CREATE_ORDER_API"), json=data)
        assert response.status_code == 400
        assert "order_table" in response.json["error"]


def test_creating_order_failed_take_away_crazy_table(app, client):
    """Test if we can create a new order unsuccessfully
    with order_table is something crazy.
    """

    with app.app_context():
        from app.query import get_or_create_user

        user_id = get_or_create_user(phone_number="12345")

        data = {
            "order_type": "take_away",
            "order_table": "Daniolo Zaniolo",
            "user": {
                "id": user_id["id"],
                "points": 20
            },
            "order_items": [
                {
                    "name": "Titanic",
                    "quantity": 1,
                    "price": .5
                },
                {
                    "name": "Olympic",
                    "quantity": 1,
                    "price": 1.5
                }
            ],
            "time_spent": "58"
        }

        # Out of range (larger than the upper bound)
        response = client.post(APIConfig.get_testing_endpoint("CREATE_ORDER_API"), json=data)
        assert response.status_code == 400
        assert "order_table" in response.json["error"]

        # Out of range (smaller than the lower bound)
        data["order_table"] = -1
        response = client.post(APIConfig.get_testing_endpoint("CREATE_ORDER_API"), json=data)
        assert response.status_code == 400
        assert "order_table" in response.json["error"]


def test_creating_order_failed_missing_items(app, client):
    """Test if we can create a new order unsuccessfully
    with informations missing order_items
    """
    with app.app_context():
        from app.query import get_or_create_user

        # We need an id..
        user_id = get_or_create_user(phone_number="12345")

        data = {
            "order_table": 1,
            "user": {
                "id": user_id["id"],
                "points": 20
            },
            "order_type": "dine_in",
            "time_spent": "58"
        }

        response = client.post(APIConfig.get_testing_endpoint("CREATE_ORDER_API"), json=data)
        assert response.status_code == 400
        assert "order_items" in response.json["error"]


def test_creating_order_failed_empty_items(app, client):
    """Test if we can create a new order unsuccessfully
    with an empty list of order_items
    """

    with app.app_context():
        from app.query import get_or_create_user

        user_id = get_or_create_user(phone_number="12345")

        data = {
            "order_table": 1,
            "user": {
                "id": user_id["id"],
                "points": 20
            },
            "order_type": "dine_in",
            "order_items": [],
            "time_spent": "58"
        }

        response = client.post(APIConfig.get_testing_endpoint("CREATE_ORDER_API"), json=data)
        assert response.status_code == 400
        assert "order_items" in response.json["error"]


def test_creating_order_failed_missing_item_name(app, client):
    """Test if we can create a new order unsuccessfully
    with a missing item name
    """

    with app.app_context():
        from app.query import get_or_create_user

        user_id = get_or_create_user(phone_number="12345")

        data = {
            "order_table": 1,
            "user": {
                "id": user_id["id"],
                "points": 20
            },
            "order_type": "dine_in",
            "order_items": [
                {
                    "quantity": 10,
                    "price": 1
                }
            ],
            "time_spent": "58"
        }

        response = client.post(APIConfig.get_testing_endpoint("CREATE_ORDER_API"), json=data)
        assert response.status_code == 400
        assert "item_name" in response.json["error"]


def test_creating_order_failed_missing_item_quantity(app, client):
    """Test if we can create a new order unsuccessfully
    with a missing item name
    """

    with app.app_context():
        from app.query import get_or_create_user

        user_id = get_or_create_user(phone_number="12345")

        data = {
            "order_table": 1,
            "user": {
                "id": user_id["id"],
                "points": 20
            },
            "order_type": "dine_in",
            "order_items": [
                {
                    "name": "Daniolo Zaniolo",
                    "price": 1
                }
            ],
            "time_spent": "58"
        }

        response = client.post(APIConfig.get_testing_endpoint("CREATE_ORDER_API"), json=data)
        assert response.status_code == 400
        assert "item_quantity" in response.json["error"]


def test_creating_order_failed_missing_item_price(app, client):
    """Test if we can create a new order unsuccessfully
    with a missing item name
    """

    with app.app_context():
        from app.query import get_or_create_user

        user_id = get_or_create_user(phone_number="12345")

        data = {
            "order_table": 1,
            "user": {
                "id": user_id["id"],
                "points": 20
            },
            "order_type": "dine_in",
            "order_items": [
                {
                    "name": "Daniolo Zaniolo",
                    "quantity": 10,
                }
            ],
            "time_spent": "58"
        }

        response = client.post(APIConfig.get_testing_endpoint("CREATE_ORDER_API"), json=data)
        assert response.status_code == 400
        assert "item_price" in response.json["error"]


def test_creating_order_failed_crazy_item_price(app, client):
    """Test if we can create a new order unsuccessfully
    with a string as item_price

    This test also check if string integer is ok.
    """

    with app.app_context():
        from app.query import get_or_create_user

        user_id = get_or_create_user(phone_number="12345")

        data = {
            "order_table": 1,
            "user": {
                "id": user_id["id"],
                "points": 20
            },
            "order_type": "dine_in",
            "order_items": [
                {
                    "name": "Daniolo Zaniolo",
                    "price": "Andrea Pirlo",
                    "quantity": "10",
                }
            ],
            "time_spent": "58"
        }

        response = client.post(APIConfig.get_testing_endpoint("CREATE_ORDER_API"), json=data)
        assert response.status_code == 400
        assert "item_price" in response.json["error"]
        assert "item_quantity" not in response.json["error"]


def test_creating_order_failed_crazy_item_quantity(app, client):
    """Test if we can create a new order unsuccessfully
    with a crazy item quantity.

    This test also check if a string price is ok.
    """

    with app.app_context():
        from app.query import get_or_create_user

        user_id = get_or_create_user(phone_number="12345")

        data = {
            "order_table": 1,
            "user": {
                "id": user_id["id"],
                "points": 20
            },
            "order_type": "dine_in",
            "order_items": [
                {
                    "name": "Daniolo Zaniolo",
                    "price": "10.5",
                    "quantity": "Andrea Pirlo",
                }
            ],
            "time_spent": "58"
        }

        response = client.post(APIConfig.get_testing_endpoint("CREATE_ORDER_API"), json=data)
        assert response.status_code == 400
        assert "item_quantity" in response.json["error"]
        assert "item_price" not in response.json["error"]


def test_creating_order_failed_missing_type(app, client):
    """Test if we can create a new order unsuccessfully
    with informations missing order_type
    """

    with app.app_context():
        from app.query import get_or_create_user

        user_id = get_or_create_user(phone_number="12345")

        data = {
            "order_table": 1,
            "user": {
                "id": user_id["id"],
                "points": 20
            },
            "order_items": [
                {
                    "name": "Titanic",
                    "quantity": 1,
                    "price": .5
                },
                {
                    "name": "Olympic",
                    "quantity": 1,
                    "price": 1.5
                }
            ],
            "time_spent": "58"
        }

        response = client.post(APIConfig.get_testing_endpoint("CREATE_ORDER_API"), json=data)
        assert response.status_code == 400
        assert "order_type" in response.json["error"]


def test_creating_order_failed_missing_time_spent(app, client):
    """Test if we can create a new order unsuccessfully
    with informations missing time_spent
    """

    with app.app_context():
        from app.query import get_or_create_user

        user_id = get_or_create_user(phone_number="12345")

        data = {
            "order_table": 1,
            "user": {
                "id": user_id["id"],
                "points": 20
            },
            "order_type": "dine_in",
            "order_items": [
                {
                    "name": "Titanic",
                    "quantity": 1,
                    "price": .5
                },
                {
                    "name": "Olympic",
                    "quantity": 1,
                    "price": 1.5
                }
            ],
        }

        response = client.post(APIConfig.get_testing_endpoint("CREATE_ORDER_API"), json=data)
        assert response.status_code == 400
        assert "time_spent" in response.json["error"]


def test_creating_order_failed_crazy_time_spent(app, client):
    """Test if we can create a new order unsuccessfully
    with crazy time_spent
    """

    with app.app_context():
        from app.query import get_or_create_user

        user_id = get_or_create_user(phone_number="12345")

        data = {
            "order_table": 1,
            "user": {
                "id": user_id["id"],
                "points": 20
            },
            "order_type": "dine_in",
            "order_items": [
                {
                    "name": "Titanic",
                    "quantity": 1,
                    "price": .5
                },
                {
                    "name": "Olympic",
                    "quantity": 1,
                    "price": 1.5
                }
            ],
            "time_spent": "Daniolo Zaniolo"
        }

        response = client.post(APIConfig.get_testing_endpoint("CREATE_ORDER_API"), json=data)
        assert response.status_code == 400
        assert "time_spent" in response.json["error"]


def test_creating_order_failed_wrong_type(app, client):
    """Test if we can create a new order unsuccessfully
    with order_type not in ["dine_in" and "take_away"]
    """
    with app.app_context():
        from app.query import get_or_create_user

        user_id = get_or_create_user(phone_number="12345")

        data = {
            "order_table": 1,
            "user": {
                "id": user_id["id"],
                "points": 20
            },
            "order_type": "dine-in",
            "order_items": [
                {
                    "name": "Titanic",
                    "quantity": 1,
                    "price": .5
                },
                {
                    "name": "Olympic",
                    "quantity": 1,
                    "price": 1.5
                }
            ],
            "time_spent": "58"
        }

        response = client.post(APIConfig.get_testing_endpoint("CREATE_ORDER_API"), json=data)
        assert response.status_code == 400
        assert "order_type" in response.json["error"]


def test_creating_order_failed_user_id_not_exist(client):
    """Test if we can create a new order unsuccessfully
    with a made-up user_id
    """

    data = {
        "order_table": 1,
        "user": {
            "id": "66666",
            "points": 20
        },
        "order_type": "dine_in",
        "order_items": [
            {
                "name": "Titanic",
                "quantity": 1,
                "price": .5
            },
            {
                "name": "Olympic",
                "quantity": 1,
                "price": 1.5
            }
        ],
        "time_spent": "58"
    }

    response = client.post(APIConfig.get_testing_endpoint("CREATE_ORDER_API"), json=data)
    assert response.status_code == 400
    assert "user_id" in response.json["error"]
