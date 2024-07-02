$(document).ready(() => {
    // Set week number onload
    let weekNumber = window.kdsUtils.getWeekNumber(new Date()).join("-W");
    $("#weekInput").val(weekNumber);
});

// Week filter button click.
$("#weekStatFilter").on("click", () => {
    // Clear errors
    $("#statFilterError").html("");

    // Get week input and validate
    let weekInput = $("#weekInput").val();

    if (weekInput.length == 0) {
        $("#statFilterError").html("Invalid input, please try again");
    } else {
        // Parse the week input to get first and last date.
        let weekDays = window.kdsUtils.parseDates(weekInput);
        let startDate = weekDays.at(0);
        let endDate = weekDays.at(-1);

        // Send request to the server to get orders in [startDay, endDay] interval.
        let request = new window.baseRequest(
            {
                url: '{{ url_for("get_order_in_range") }}',
                type: "POST",
                dataType: "json",
                contentType: "application/json",
                data: JSON.stringify({
                    start_date: startDate,
                    end_date: endDate,
                    table_list: [],
                    mode_list: [],
                    status_list: [],
                }),
            },
            sendWeekStatRequestSuccessCallbackFn,
            sendWeekStatRequestFailedCallbackFn
        );

        request.send();
    }
});

/**
 * Callback function to a successful send week stat request.
 * @param {Object} response
 * @param {Object} textStatus
 * @param {Object} jqXHR
 */
const sendWeekStatRequestSuccessCallbackFn = (response, textStatus, jqXHR) => {
    let orderList = response["order_list"];
    let statTemplate = new window.statTemplate(orderList);
    let graphTemplate = new window.graph(orderList);

    if (statTemplate.totalOrders() == 0) {
        $("#weekStatsContent").html("No results");
    } else {
        // Append the stats header
        $("#weekStatsContent").html(statTemplate.getHTML());

        // Append the pie chart and the histogram
        let contentRow = $(document.createElement("div"));
        contentRow.addClass("row");

        contentRow.append(graphTemplate.getPieSummarizeHTML());
        contentRow.append(
            graphTemplate.getHistBestSellerHTML(
                window.kdsUtils.MAX_BEST_SELLER_ITEMS
            )
        );

        $("#weekStatsContent").append(contentRow);

        // Append the last line chart
        $("#weekStatsContent").append(
            graphTemplate.getLineItemPerWeekdaysHTML()
        );
    }
};

/**
 * Callback function to a failed send week stat request.
 * @param {Object} jqXHR
 * @param {Object} textStatus
 * @param {Object} errorThrown
 */
const sendWeekStatRequestFailedCallbackFn = (
    jqXHR,
    textStatus,
    errorThrown
) => {
    $("#statFilterError").html("Error occurs, please try again later.");
};
