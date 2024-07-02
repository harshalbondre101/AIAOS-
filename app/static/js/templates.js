
/**
 * One Order Template for multiple-way rendering
 *
 */
export class OrderTemplate {
    /**
     * Constructor for the Order Template class.
     * @param {Object} order object
     */
    constructor(order) {
        this._orderId = order.order_id;
        this._orderStatus = order.order_status;
        this._orderMode = order.order_mode;
        this._orderCreationDate = order.order_creation_date;
        this._orderFinishDate = order.order_finish_date;
        this._orderTable = order.order_table;
        this._orderItems = order.order_items;
        this._orderButtons = order.buttons;
        this._orderHistoryTotalPrice = this._orderItems
            .filter(
                (a) =>
                    a.item_status == window.kdsUtils.ORDER_ITEM_FINISHED_STATUS
            )
            .map((b) => b.item_quantity * b.item_price)
            .reduce((c, d) => c + d, 0);

        // Some orders does not have username.
        if (order.user_name) {
            this._userName = order.user_name;
        }
    }

    /**
     * Render the order using the Dine In template.
     * @returns {str} HTML string of the Dine In template
    */
    getDineInHTML() {
        // console.log(this._orderButtons)
        let card = $(document.createElement("div"));
        card.attr("order_id", this._orderId);
        card.addClass("card card-dinein-order border-primary");

        // Card header
        let cardHeader = $(document.createElement("div"));

        cardHeader.addClass("card-header");

        let orderName = $(document.createElement("h5"));
        orderName.text("Order " + this._orderId);
        orderName.addClass("page-title float-start");

        let orderCreationDate = $(document.createElement("p"));
        orderCreationDate.text(this._orderCreationDate);
        orderCreationDate.addClass("float-end");

        cardHeader.append(orderName);
        cardHeader.append(orderCreationDate);

        card.append(cardHeader);

        // Card body
        let cardBody = $(document.createElement("div"));
        cardBody.addClass("card-body");

        // Order detail (list of items)
        for (let i = 0; i < this._orderItems.length; ++i) {
            let currentItem = $(document.createElement("div"));
            currentItem.addClass("row");

            // Current item name (pull to the left)
            let currentItemNameWrapper = $(document.createElement("p"));
            currentItemNameWrapper.addClass("col text-start");

            let currentItemName = $(document.createElement("div"));
            currentItemName.addClass("form-check form-inline checkbox-xl");

            // Current item checkbox
            let currentItemCheckbox = $(document.createElement("input"));
            currentItemCheckbox.attr("type", "checkbox");
            currentItemCheckbox.attr("item_id", this._orderItems[i].id);
            currentItemCheckbox.attr(
                "id",
                "checkbox_item_" + this._orderItems[i].id
            );
            currentItemCheckbox.addClass("form-check-input item-check");

            // In case of incomplete order, this to make sure delivered / canceled items
            // still counted.
            if (
                this._orderItems[i].status ==
                window.kdsUtils.ORDER_ITEM_FINISHED_STATUS
            ) {
                currentItemCheckbox.attr("checked", true);
            }

            // Current item label
            let currentItemLabel = $(document.createElement("label"));
            currentItemLabel.addClass("form-check-label");
            currentItemLabel.attr(
                "for",
                "checkbox_item_" + this._orderItems[i].id
            );
            currentItemLabel.attr(
                "id",
                "checkbox_item_label_" + this._orderItems[i].id
            );
            currentItemLabel.html("<b>" + this._orderItems[i].name + "</b>");

            // In case of incomplete order, this to make sure delivered / canceled items
            // still counted.
            if (
                this._orderItems[i].status ==
                window.kdsUtils.ORDER_ITEM_FINISHED_STATUS
            ) {
                currentItemLabel.addClass("strike text-success");
            }
            if (
                this._orderItems[i].status ==
                window.kdsUtils.ORDER_ITEM_CANCELED_STATUS
            ) {
                currentItemLabel.addClass("strike text-danger");
            }

            currentItemName.append(currentItemCheckbox);
            currentItemName.append(currentItemLabel);

            currentItemNameWrapper.append(currentItemName);

            // Current item quantity (pull to the right)
            let currentItemQuantityWrapper = $(document.createElement("p"));
            currentItemQuantityWrapper.addClass("col text-end");

            // Remove button
            let currentItemRemoveButton = $(document.createElement("button"));
            currentItemRemoveButton.attr("type", "button");
            currentItemRemoveButton.attr("item_id", this._orderItems[i].id);
            currentItemRemoveButton.attr(
                "id",
                "remove_item_" + this._orderItems[i].id
            );
            currentItemRemoveButton.attr("aria-label", "Remove");
            currentItemRemoveButton.addClass("btn-close item-remove");

            let currentItemQuantity = $(document.createElement("b"));
            currentItemQuantity.addClass("item-quantity");
            currentItemQuantity.attr(
                "id",
                "item_quantity_" + this._orderItems[i].id
            );
            currentItemQuantity.text(this._orderItems[i].quantity);

            // In case of incomplete order, this to make sure delivered / canceled items
            // still counted.
            if (
                this._orderItems[i].status ==
                window.kdsUtils.ORDER_ITEM_FINISHED_STATUS
            ) {
                currentItemQuantity.addClass("strike text-success");
            }
            if (
                this._orderItems[i].status ==
                window.kdsUtils.ORDER_ITEM_CANCELED_STATUS
            ) {
                currentItemQuantity.addClass("strike text-danger");
            }

            currentItemQuantityWrapper.append(currentItemQuantity);
            currentItemQuantityWrapper.append(currentItemRemoveButton);

            currentItem.append(currentItemNameWrapper);
            currentItem.append(currentItemQuantityWrapper);

            cardBody.append(currentItem);
        }

        card.append(cardBody);

        // Footer with the "Finish" button
        let cardFooter = $(document.createElement("div"));
        cardFooter.addClass("d-flex justify-content-center");
        cardFooter.addClass("card-footer");

        let finishButton = $(document.createElement("button"));
        finishButton.addClass(
            "btn-finish btn-dinein btn btn-success float-start"
        );
        finishButton.text("Finished");
        
        let userActionsButton = $(document.createElement("button"));
        userActionsButton.addClass(
            "btn-useractions btn-dinein btn btn-info mx-auto"
        );
        userActionsButton.text("User Actions")

        let cancelButton = $(document.createElement("button"));
        cancelButton.addClass("btn-cancel btn-dinein btn btn-danger float-end");
        cancelButton.text("Cancel");

        cardFooter.append(finishButton);
        cardFooter.append(userActionsButton);
        cardFooter.append(cancelButton);
        card.append(cardFooter);

        return card;
    }
        

    /**
     * Render the order using the Take Away template.
     * @returns {str} HTML string of the Take Away template
     */
    getTakeAwayHTML() {
        let card = $(document.createElement("div"));
        
        card.attr("order_id", this._orderId);
        card.addClass(
            "card col-xs-5 col-md-5 col-lg-5 col-md-5 border-primary"
        );

        // Card header
        let cardHeader = $(document.createElement("div"));
        

        cardHeader.addClass(
            "card-header card-order-history-collapse collapsed"
        );
        cardHeader.attr("data-bs-toggle", "collapse");
        cardHeader.attr("href", "#card_order_" + this._orderId);
        cardHeader.attr("role", "button");
        cardHeader.attr("aria-expanded", "false");
        cardHeader.attr("aria-controls", "card_order_" + this._orderId);

        let orderTableCard = $(document.createElement("h5"));
        orderTableCard.addClass("float-start");
        orderTableCard.text(this._userName + " (" + this._orderTable + ")");

        let orderCreationCard = $(document.createElement("p"));
        orderCreationCard.addClass("float-end");
        orderCreationCard.text(this._orderCreationDate);

        cardHeader.append(orderTableCard);
        cardHeader.append(orderCreationCard);

        card.append(cardHeader);

        // Card body
        let cardBody = $(document.createElement("div"));
        
        cardBody.addClass("d-flex justify-content-center");
        cardBody.addClass("card-body collapse");
        cardBody.attr("id", "card_order_" + this._orderId);

        // Order detail (list of items)
        let cardList = $(document.createElement("div"));
        cardList.addClass("takeaway-items");
        for (let i = 0; i < this._orderItems.length; ++i) {
            let currentItem = $(document.createElement("div"));
            currentItem.addClass("row");

            // Current item name (pull to the left)
            let currentItemNameWrapper = $(document.createElement("div"));
            currentItemNameWrapper.addClass("col text-start");

            let currentItemName = $(document.createElement("div"));
            currentItemName.addClass("form-check form-inline checkbox-xl");

            // Current item checkbox
            let currentItemCheckbox = $(document.createElement("input"));
            currentItemCheckbox.attr("type", "checkbox");
            currentItemCheckbox.attr("item_id", this._orderItems[i].item_id);
            currentItemCheckbox.attr(
                "id",
                "checkbox_item_" + this._orderItems[i].item_id
            );
            currentItemCheckbox.addClass("form-check-input item-check");

            // Current item label
            let currentItemLabel = $(document.createElement("label"));
            currentItemLabel.addClass("form-check-label");
            currentItemLabel.attr(
                "for",
                "checkbox_item_" + this._orderItems[i].item_id
            );
            currentItemLabel.attr(
                "id",
                "checkbox_item_label_" + this._orderItems[i].item_id
            );
            currentItemLabel.html(
                "<b>" + this._orderItems[i].item_name + "</b>"
            );

            currentItemName.append(currentItemCheckbox);
            currentItemName.append(currentItemLabel);

            currentItemNameWrapper.append(currentItemName);

            // Current item quantity (pull to the right)
            let currentItemQuantityWrapper = $(document.createElement("div"));
            currentItemQuantityWrapper.addClass("col text-end");

            // Remove button
            let currentItemRemoveButton = $(document.createElement("button"));
            currentItemRemoveButton.attr("type", "button");
            currentItemRemoveButton.attr(
                "item_id",
                this._orderItems[i].item_id
            );
            currentItemRemoveButton.attr(
                "id",
                "remove_item_" + this._orderItems[i].item_id
            );
            currentItemRemoveButton.attr("aria-label", "Remove");
            currentItemRemoveButton.addClass("btn-close item-remove");

            let currentItemQuantity = $(document.createElement("b"));
            currentItemQuantity.addClass("item-quantity");
            currentItemQuantity.attr(
                "id",
                "item_quantity_" + this._orderItems[i].item_id
            );
            currentItemQuantity.text(this._orderItems[i].item_quantity);

            currentItemQuantityWrapper.append(currentItemQuantity);
            currentItemQuantityWrapper.append(currentItemRemoveButton);

            currentItem.append(currentItemNameWrapper);
            currentItem.append(currentItemQuantityWrapper);

            cardList.append(currentItem);
        }

        cardBody.append(cardList);

        // Footer with the "Finish" button
        let finishButton = $(document.createElement("button"));
        finishButton.addClass(
            "btn-finish btn-takeaway btn btn-success float-start"
        );
        finishButton.text("Finished");

        let userActionsButton = $(document.createElement("button"));
        userActionsButton.addClass(
            "btn-useractions btn-takeaway btn btn-info float-start"
        );
        userActionsButton.text("User Actions");

        let cancelButton = $(document.createElement("button"));
        cancelButton.addClass(
            "btn-cancel btn-takeaway btn btn-danger float-end"
        );
        cancelButton.text("Cancel");

        cardBody.append(finishButton);
        cardBody.append(userActionsButton);
        cardBody.append(cancelButton);

        card.append(cardBody);

        return card;
    }




    /**
     * Render the order using the history template.
     * @returns {str} HTML string of the History template
     */
    getHistoryHTML() {
        let card = $(document.createElement("div"));
        card.attr("order_id", this._orderId);
        card.addClass("card border-primary");

        // Card header
        let cardHeader = $(document.createElement("div"));
        cardHeader.addClass(
            "card-header card-order-history-collapse collapsed"
        );
        cardHeader.attr("data-bs-toggle", "collapse");
        cardHeader.attr("href", "#card_order_" + this._orderId);
        cardHeader.attr("role", "button");
        cardHeader.attr("aria-expanded", "false");
        cardHeader.attr("aria-controls", "card_order_" + this._orderId);

        let orderClass;
        if (this._orderStatus == window.kdsUtils.ORDER_INPROGRESS_STATUS) {
            orderClass = "bg-info text-black";
        } else if (this._orderStatus == window.kdsUtils.ORDER_FINISHED_STATUS) {
            orderClass = "bg-success text-white";
        } else if (this._orderStatus == window.kdsUtils.ORDER_CANCELED_STATUS) {
            orderClass = "bg-danger text-white";
        } else if (this._orderStatus == window.kdsUtils.ORDER_REFUNDED_STATUS) {
            orderClass = "bg-warning text-black";
        }

        cardHeader.addClass(orderClass);

        let cardOrderId = $(document.createElement("h5"));
        cardOrderId.addClass("page-title float-start");

        if (this._orderMode == window.kdsUtils.ORDER_TABLE_DINEIN) {
            cardOrderId.text("Table " + this._orderTable);
        } else if (this._orderMode == window.kdsUtils.ORDER_TABLE_TAKEAWAY) {
            cardOrderId.text("Order " + this._orderTable);
        }

        let cardOrderMode = $(document.createElement("p"));
        cardOrderMode.addClass("float-end");
        cardOrderMode.text(this._orderMode.replace("_", " "));

        cardHeader.append(cardOrderId);
        cardHeader.append(cardOrderMode);

        card.append(cardHeader);

        // Card body
        let cardBody = $(document.createElement("div"));
        cardBody.addClass("card-body collapse");
        cardBody.attr("id", "card_order_" + this._orderId);

        // Order creation & finish date.
        let dateWrapper = $(document.createElement("p"));

        let cardOrderCreationDate = $(document.createElement("span"));
        cardOrderCreationDate.addClass("float-start order-get-date");
        cardOrderCreationDate.html("<b>Get:</b> " + this._orderCreationDate);

        let cardOrderFinishDate = $(document.createElement("span"));
        cardOrderFinishDate.addClass("float-end order-finish-date");
        if (this._orderStatus == window.kdsUtils.ORDER_INPROGRESS_STATUS) {
            cardOrderFinishDate.html("<b>Ongoing</b>");
        } else if (this._orderStatus == window.kdsUtils.ORDER_FINISHED_STATUS) {
            cardOrderFinishDate.html("<b>Done:</b> " + this._orderFinishDate);
        } else if (this._orderStatus == window.kdsUtils.ORDER_CANCELED_STATUS) {
            cardOrderFinishDate.html(
                "<b>Canceled:</b> " + this._orderFinishDate
            );
        } else if (this._orderStatus == window.kdsUtils.ORDER_REFUNDED_STATUS) {
            cardOrderFinishDate.html(
                "<b>Refunded:</b> " + this._orderFinishDate
            );
        }

        dateWrapper.append(cardOrderCreationDate);
        dateWrapper.append(cardOrderFinishDate);

        let cardWrapper = $(document.createElement("p"));
        cardWrapper.addClass("card-order-history-body-item-wrapper");

        let cardList = $(document.createElement("ul"));
        for (let i = 0; i < this._orderItems.length; ++i) {
            let currentItem = $(document.createElement("li"));

            let currentItemName = $(document.createElement("span"));
            currentItemName.addClass("float-start");
            currentItemName.html(
                "<b>" +
                    this._orderItems[i].item_name +
                    " (" +
                    window.kdsUtils.CURRENCY +
                    " " +
                    this._orderItems[i].item_price.toFixed(
                        window.kdsUtils.CURRENCY_DIGIT_PRECISION
                    ) +
                    ") </b>"
            );

            // Format to show which item is delivered / canceled
            if (
                this._orderItems[i].item_status ==
                window.kdsUtils.ORDER_ITEM_FINISHED_STATUS
            ) {
                currentItemName.addClass("text-success");
            }
            if (
                this._orderItems[i].item_status ==
                window.kdsUtils.ORDER_ITEM_CANCELED_STATUS
            ) {
                currentItemName.addClass("text-danger");
            }

            // Gift, can be replace to ignore it.
            if (this._orderItems[i].item_price == 0) {
                let giftBadge = $(document.createElement("span"));
                giftBadge.addClass("badge bg-success");
                giftBadge.html("Gift");

                currentItemName.append(giftBadge);
            }

            let currentItemQuantity = $(document.createElement("span"));
            currentItemQuantity.addClass("float-end");
            currentItemQuantity.html(
                "<b>" + this._orderItems[i].item_quantity + "</b>"
            );

            // Format to show which item is delivered / canceled
            if (
                this._orderItems[i].item_status ==
                window.kdsUtils.ORDER_ITEM_FINISHED_STATUS
            ) {
                currentItemQuantity.addClass("text-success");
            }
            if (
                this._orderItems[i].item_status ==
                window.kdsUtils.ORDER_ITEM_CANCELED_STATUS
            ) {
                currentItemQuantity.addClass("text-danger");
            }

            currentItem.append(currentItemName);
            currentItem.append(currentItemQuantity);

            cardList.append(currentItem);
        }
        cardWrapper.append(cardList);

        // Total - at the end of the card
        let totalWrapper = $(document.createElement("p"));
        let totalLabel = $(document.createElement("span"));
        totalLabel.addClass("float-start");
        totalLabel.html("<b>Total</b>");

        let totalAmount = $(document.createElement("span"));
        totalAmount.addClass("float-end");
        totalAmount.html(
            "<b>" +
                window.kdsUtils.CURRENCY +
                " " +
                this._orderHistoryTotalPrice.toFixed(
                    window.kdsUtils.CURRENCY_DIGIT_PRECISION
                ) +
                "</b>"
        );

        totalWrapper.append(totalLabel);
        totalWrapper.append(totalAmount);

        let divider = $(document.createElement("hr"));

        cardBody.append(dateWrapper);
        cardBody.append(cardWrapper);
        cardBody.append(divider);
        cardBody.append(totalWrapper);

        // Refund button, for success order only.
        if (this._orderStatus == window.kdsUtils.ORDER_FINISHED_STATUS) {
            let refundButton = $(document.createElement("button"));
            refundButton.addClass("btn btn-warning btn-refund");
            refundButton.attr("data-bs-toggle", "modal");
            refundButton.attr("data-bs-target", "#pinModal");
            refundButton.text("Refund");
            cardBody.append("<br/>");
            cardBody.append(refundButton);
        }

        card.append(cardBody);

        return card;
    }
}

/**
 * Stats header template
 *
 */
export class StatsHeaderTemplate {
    /**
     * Constructor
     * @param {Object} orderList
     */
    constructor(orderList) {
        this._totalOrders = orderList.length;

        // Count list of order types.
        this._totalInProgressOrders = orderList.filter(
            (x) => x.order_status == window.kdsUtils.ORDER_INPROGRESS_STATUS
        ).length;

        this._totalFinishedOrders = orderList.filter(
            (x) => x.order_status == window.kdsUtils.ORDER_FINISHED_STATUS
        ).length;

        this._totalCanceledOrders = orderList.filter(
            (x) => x.order_status == window.kdsUtils.ORDER_CANCELED_STATUS
        ).length;

        this._totalRefundedOrders = orderList.filter(
            (x) => x.order_status == window.kdsUtils.ORDER_REFUNDED_STATUS
        ).length;

        // Calculate total prices
        this._totalOrdersPrice = orderList
            .filter(
                (v) => v.order_status == window.kdsUtils.ORDER_FINISHED_STATUS
            )
            .map((x) => x.order_items)
            .flat()
            .filter(
                (y) =>
                    y.item_status == window.kdsUtils.ORDER_ITEM_FINISHED_STATUS
            )
            .map((z) => z.item_price * z.item_quantity)
            .reduce((t, u) => t + u, 0);
    }

    /**
     * Total orders
     * @returns {Number}
     */
    totalOrders() {
        return this._totalOrders;
    }

    /**
     * Calculate fee to pay.
     * @param {Number} fee Percent to pay
     * @returns {Number} Calculate the fee to pay from total orders.
     */
    calculateFee(fee = window.kdsUtils.AIAOS_FEE) {
        return this._totalOrdersPrice * fee;
    }

    /**
     * Generate the stat header.
     * @returns {String} HTML template of the stat header.
     */
    getHTML() {
        let statDiv = $(document.createElement("div"));
        statDiv.addClass("stat-header");

        // Count total orders
        let historyTotalOrders = $(document.createElement("p"));
        historyTotalOrders.html(
            "<b>Total orders in range: " + this._totalOrders + " </b>"
        );

        // Details of stats
        let historyStats = $(document.createElement("ul"));

        // Finished orders
        let historyStatsFinished = $(document.createElement("li"));
        historyStatsFinished.html(
            "<b>" + this._totalFinishedOrders + " finished orders</b>"
        );
        historyStatsFinished.addClass("text-success");

        // Canceled orders
        let historyStatsCanceled = $(document.createElement("li"));
        historyStatsCanceled.html(
            "<b>" + this._totalCanceledOrders + " canceled orders</b>"
        );
        historyStatsCanceled.addClass("text-danger");

        // Refunded orders
        let historyStatsRefunded = $(document.createElement("li"));
        historyStatsRefunded.html(
            "<b>" + this._totalRefundedOrders + " refunded orders</b>"
        );
        historyStatsRefunded.addClass("text-warning");

        // In progress orders
        let historyStatsInProgress = $(document.createElement("li"));
        historyStatsInProgress.html(
            "<b>" + this._totalInProgressOrders + " in progress orders</b>"
        );
        historyStatsInProgress.addClass("text-info");

        historyStats.append(historyStatsFinished);
        historyStats.append(historyStatsCanceled);
        historyStats.append(historyStatsRefunded);
        historyStats.append(historyStatsInProgress);

        // Total sales
        let historyTotalPrice = $(document.createElement("p"));
        historyTotalPrice.html(
            "<b>Total sales in range: " +
                window.kdsUtils.CURRENCY +
                " " +
                this._totalOrdersPrice.toFixed(
                    window.kdsUtils.CURRENCY_DIGIT_PRECISION
                ) +
                "</b>"
        );

        // 1% of the sales
        let historyOnePercentPrice = $(document.createElement("p"));
        historyOnePercentPrice.html(
            "<b>AIAOs fee: " +
                window.kdsUtils.CURRENCY +
                " " +
                this.calculateFee().toFixed(
                    window.kdsUtils.CURRENCY_DIGIT_PRECISION
                ) +
                "</b>"
        );

        let divider = $(document.createElement("hr"));

        statDiv.append(historyTotalOrders);
        statDiv.append(historyStats);
        statDiv.append(historyTotalPrice);
        statDiv.append(historyOnePercentPrice);
        statDiv.append(divider);

        return statDiv;
    }
}
