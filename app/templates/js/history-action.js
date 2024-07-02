// Automatically update the end date if chosing start date without end date
$("#filterStart").on("change", () => {
    let filterStartDate = $("#filterStart").val();
    let filterEndDate = $("#filterEnd").val();

    if (filterEndDate.length == 0 && filterStartDate.length > 0) {
        $("#filterEnd").val(filterStartDate);
    }
});

// Automatically update the start date if chosing end date without start date
$("#filterEnd").on("change", () => {
    let filterStartDate = $("#filterStart").val();
    let filterEndDate = $("#filterEnd").val();

    if (filterStartDate.length == 0 && filterEndDate.length > 0) {
        $("#filterStart").val(filterEndDate);
    }
});

// Button filter click
$("#startFilter").on("click", () => {
    // Disable filter button to prevent spamming
    $("#startFilter").prop("disabled", true);
    $("#startFilterBtnSpinner").removeClass("visually-hidden");
    $("#startFilterBtnText").text("Filtering..");

    // Reset error text
    $("#filterError").text("");

    // Get values
    let startDate = $("#filterStart").val();
    let endDate = $("#filterEnd").val();
    let listTable = $("#filterTable").val();

    // Mode from the checkbox.
    let listMode = [];

    if ($("#dineInType").is(":checked")) {
        listMode.push(window.kdsUtils.ORDER_TABLE_DINEIN);
    }

    if ($("#takeAwayType").is(":checked")) {
        listMode.push(window.kdsUtils.ORDER_TABLE_TAKEAWAY);
    }

    let listStatus = $("#filterStatus").val();

    // Date validation (not empty)
    if (startDate.length == 0 || endDate.length == 0) {
        $("#filterError").text("Start date / end date not valid");
    }

    // Send query request.
    else {
        let request = new window.baseRequest(
            {
                url: '{{ url_for("get_order_in_range") }}',
                type: "POST",
                dataType: "json",
                contentType: "application/json",
                data: JSON.stringify({
                    start_date: startDate,
                    end_date: endDate,
                    table_list: listTable,
                    mode_list: listMode,
                    status_list: listStatus,
                }),
            },
            sendQueryRangeRequestSuccessCallbackFn,
            sendQueryRangeRequestFailedCallbackFn
        );
        request.send();
    }

    // Enable the filter button afterward.
    $("#startFilterBtnSpinner").addClass("visually-hidden");
    $("#startFilterBtnText").text("Filter");
    $("#startFilter").prop("disabled", false);
});

// Handle the "refund" button click
$("#history_board").on("click", "button.btn.btn-refund", function () {
    // Get current order id
    let currentOrderId = $(this).parent().parent().attr("order_id");

    // Reset the PIN
    pinLogin.reset();

    // Clear the input error
    $("#pinError").html("");

    // Set order_id for the modal
    $("#pinModalLabel").html(currentOrderId);

    // Show the modal
    pinModalInstance.show($("#pinModal"));
});

// Handle the PIN confirm button - send request and do the rest.
$(".btn-pin-confirm").on("click", () => {
    let currentOrderId = $("#pinModalLabel").text();
    let currentPin = pinLogin.values.toString().split(",").join("");

    // Clear PIN
    pinLogin.reset();

    // Send a refund request.
    let request = new window.baseRequest(
        {
            url: '{{ url_for("order_refund") }}',
            type: "POST",
            dataType: "json",
            contentType: "application/json",
            data: JSON.stringify({
                order_id: currentOrderId,
                pincode: currentPin,
            }),
        },
        sendRefundRequestSuccessCallbackFn,
        sendRefundRequestFailedCallbackFn
    );
    request.send();
});

/**
 * Callback function for a success query range request/
 * @param {Object} response
 * @param {Object} textStatus
 * @param {Object} jqXHR
 */
const sendQueryRangeRequestSuccessCallbackFn = (
    response,
    textStatus,
    jqXHR
) => {
    let orderList = response["order_list"];
    let statTemplate = new window.statTemplate(orderList);

    // Clear the history content page.
    $("#history_board").html("");

    if (statTemplate.totalOrders() == 0) {
        $("#history_board").html("No result found.");
    } else {
        $("#history_board").append(statTemplate.getHTML());

        // Display list of orders.
        for (let i = 0; i < orderList.length; ++i) {
            let currentOrderTemplate = new window.orderTemplate(orderList[i]);

            $("#history_board").append(currentOrderTemplate.getHistoryHTML());
        }
    }
};

/**
 * Callback function for a failed query range request.
 * @param {Object} jqXHR
 * @param {Object} textStatus
 * @param {Object} errorThrown
 */
const sendQueryRangeRequestFailedCallbackFn = (
    jqXHR,
    textStatus,
    errorThrown
) => {
    $("#history_board").html("No result found.");
    $("#filterError").text(jqXHR.responseJSON.error);
};

/**
 * Callback function for a successful refund request.
 * @param {Object} response
 * @param {Object} textStatus
 * @param {Object} jqXHR
 */
const sendRefundRequestSuccessCallbackFn = (response, textStatus, jqXHR) => {
    let modifiedDate = response["modified_date"];
    let currentOrderId = response["order_id"];
    let currentOrderCard = $("div[order_id=" + currentOrderId + "]");

    // Change card color to yellow (warning)
    currentOrderCard
        .children(".bg-success")
        .removeClass("bg-success text-white")
        .addClass("bg-warning text-black");

    // Update refund date
    $(
        "#card_order_" +
            currentOrderId +
            "> p:nth-child(1) > span.float-end.order-finish-date"
    ).html("<b>Refunded:</b> " + modifiedDate);

    // Remove refund button
    $("#card_order_" + currentOrderId + "> button.btn-refund").remove();

    // Close the PIN modal
    pinModalInstance.hide($("#pinModal"));
};

/**
 * Callback funciton for a failed refund request
 * @param {Object} jqXHR
 * @param {Object} textStatus
 * @param {Object} errorThrown
 */
const sendRefundRequestFailedCallbackFn = (jqXHR, textStatus, errorThrown) => {
    $("#pinError").text(jqXHR.responseJSON.error);
};
