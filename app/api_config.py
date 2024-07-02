class APIConfig:
    """Configurations for API

    Methods:
        get_resource_endpoint():
            return the resource endpoint (i.e. the endpoint only)

        get_testing_endpoint():
            return the full url endpoint (i.e. the prefix + endpoint) 
    """

    # Prefix of the API
    PREFIX = "/api/v1/"

    # Map of endpoints
    ENDPOINTS = {
        "GET_USER_API": "user/get",
        "GET_USER_NAME_API": "user/name",
        "UPDATE_USER_NAME_API": "user/name",
        "CREATE_ORDER_API": "order/create",
        "FINISH_ORDER_API": "order/finish",
        "CANCEL_ORDER_API": "order/cancel",
        "REFUND_ORDER_API": "order/refund",
        "FINISH_ITEM_API": "order/item/finish",
        "CANCEL_ITEM_API": "order/item/cancel",
        "GET_SINGLE_TABLE_API": "order/get",
        "GET_ORDER_IN_RANGE_API": "order/getrange",
        "CREATE_USER_ACTIONS" : "user/actions",
        "GET_USER_ACTIONS" : "get/actions"
    }

    @staticmethod
    def get_resource_endpoint(endpoint_name: str) -> str:
        """Get the resource endpoint

        Args:
            endpoint_name (str): The endpoint name

        Returns:
            str: The following endpoint value
        """
        routing_endpoint = APIConfig.ENDPOINTS.get(endpoint_name, None)
        return routing_endpoint

    @staticmethod
    def get_testing_endpoint(endpoint_name: str) -> str:
        """Get the testing endpoint

        Args:
            endpoint_name (str): The endpoint name

        Returns:
            str: The full endpoint for testing (prefix/endpoint)
        """
        testing_endpoint = f"{APIConfig.PREFIX}{APIConfig.ENDPOINTS.get(endpoint_name, None)}"
        return testing_endpoint
