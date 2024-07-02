class Utils:
    """Misc utility class.
    """

    # Default maximum tables of a restaurant
    DEFAULT_MAX_TABLE = 10

    # Default maximum tables of a display row
    DEFAULT_MAX_TABLE_PER_ROW = 5

    # Default maximum best sellers to recommends
    DEFAULT_MAX_BESTSELLER_RECOMMEND = 5

    # Default USERNAME
    DEFAULT_USERNAME = "(Not set)"

    # Default TIMEZONE
    DEFAULT_TIMEZONE = "Asia/Ho_Chi_Minh"

    # Default PINCODE
    DEFAULT_PINCODE = "131337"

    # Default SECRET_KEY
    DEFAULT_SECRET_KEY = "dev"


class OrderUtils:
    """Utility class.

    ...

    Methods
    -------
    available_order_types():
        Get available order types
    """

    # Constants string for order type
    DINEIN_ORDER_TYPE = "dine_in"
    TAKEAWAY_ORDER_TYPE = "take_away"

    # Constants string for order status
    IN_PROGRESS_ORDER_STATUS = "0"
    FINISHED_ORDER_STATUS = "1"
    CANCELED_ORDER_STATUS = "2"
    REFUNDED_ORDER_STATUS = "3"

    # Constants string for item status
    IN_PROGRESS_ITEM_STATUS = "0"
    FINISHED_ITEM_STATUS = "1"
    CANCELED_ITEM_STATUS = "2"

    @staticmethod
    def available_order_types() -> list:
        """Get available order types

        Returns:
            `available_types` (list):
                Available order types
        """

        available_types = [OrderUtils.DINEIN_ORDER_TYPE,
                           OrderUtils.TAKEAWAY_ORDER_TYPE]
        return available_types
