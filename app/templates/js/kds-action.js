// Click and choose a table to view its orders.
$(".btn-table").on("click", function () {
    let currentTable = $(this).attr("table-id");

    // Set text for the modal label.
    $("#tableModalLabel").text(currentTable);

    // Loading icon
    let spinnerDiv = $(document.createElement("div"));
    spinnerDiv.addClass("spinner-border spinner-border-sm");
    spinnerDiv.attr("role", "status");

    // Set loading icon.
    $("#tableModelListOrders").html(spinnerDiv);

    // Send request to the table API.
    let request = new window.baseRequest(
        {
            url: '{{ url_for("get_single_order") }}',
            type: "POST",
            dataType: "json",
            contentType: "application/json",
            data: JSON.stringify({
                table_id: currentTable,
            }),
        },
        getOrdersOfATableSuccessCallbackFn
    );
    request.send();
});


// We need this to catch onClick events on dynamically created elements.
// Dinein finish button.
$("#dynamic_content").on(
    "click",
    "button.btn-dinein.btn-finish",
    function (event) {
        console.log("Finish Button clicked");

        // Get table id
        var table_id = $("#tableModalLabel").text();
        console.log("table id:", table_id);
        console.log("Table id fetched");

        var formData = {
            table_id: table_id
        };

        $.ajax({
            type: 'POST',
            url: '/auto_update_inventory',
            contentType: 'application/json',
            data: JSON.stringify(formData),
            success: function(response) {
                console.log("Inventory updated successfully");

                // Use event.target to avoid scope issues inside the success callback
                let parentCard = $(event.target).closest('.card-dinein-order');
                let parentButtonTable = $("#tableModalLabel").text();
                let parentButton = $("#table_id_" + parentButtonTable);
                let parentButtonBadge = $("#table_id_" + parentButtonTable + "_badge");

                let currentId = parentCard.attr("order_id");
                let request = new window.baseRequest({
                    url: '{{ url_for("order_finish") }}',
                    type: "POST",
                    dataType: "json",
                    contentType: "application/json",
                    data: JSON.stringify({
                        order_id: currentId,
                    }),
                });
                request.send();

                // Remove finished parentCard
                parentCard.remove();

                let orderList = $("#tableModelListOrders");
                if (orderList.children().length === 0) {
                    orderList.html("No orders");

                    parentButton.removeClass("btn-success").addClass("btn-secondary");
                    parentButtonBadge.attr("value", "");
                } else {
                    let listRemainOrders = $(".card-dinein-order")
                        .map(function (_, x) {
                            return $(x).attr("order_id");
                        })
                        .get()
                        .join(" ");
                    parentButtonBadge.attr("value", listRemainOrders);
                }

                // Re-indexing all current available items
                window.kdsUtils.reIndexing();

                // Re-count all current orders
                window.kdsUtils.reCountOrders(window.kdsUtils.ORDER_TABLE_DINEIN);

            },
            error: function(xhr, status, error) {
                var errorMessage = JSON.parse(xhr.responseText).error;
                console.log("Error: " + errorMessage);
            }
        });
    }
);

$("#dynamic_content").on(
    "click",
    "button.btn-dinein.btn-useractions",
    function (event) {
        let parentCard = $(this).closest('.card-dinein-order');
        let parentButtonTable = $("#tableModalLabel").text();
        let parentButton = $("#table_id_" + parentButtonTable);
        let parentButtonBadge = $("#table_id_" + parentButtonTable + "_badge");

        let currentId = parentCard.attr("order_id");
        let form = $("<form>", {
            method: "POST",
            action: '{{ url_for("order_actions") }}',
            target: "_blank",  // Open in a new tab or window
        });

        // Add an input field with the order_id value
        $("<input>").attr({
            type: "hidden",
            name: "order_id",
            value: currentId,
        }).appendTo(form);

        // Append the form to the body and submit it
        form.appendTo("body").submit();
    }
);



// Dinein cancel button
$("#dynamic_content").on(
    "click",
    "button.btn-dinein.btn-cancel",
    function (event) {
        let parentCard = $(this).parent().parent();
        let parentButtonTable = $("#tableModalLabel").text();
        let parentButton = $("#table_id_" + parentButtonTable);
        let parentButtonBadge = $("#table_id_" + parentButtonTable + "_badge");

        // Add api to remove here
        let currentId = parentCard.attr("order_id");

        let request = new window.baseRequest({
            url: '{{ url_for("order_cancel") }}',
            type: "POST",
            dataType: "json",
            contentType: "application/json",
            data: JSON.stringify({
                order_id: currentId,
            }),
        });
        request.send();

        // Remove finished parentCard
        parentCard.remove();

        let orderList = $("#tableModelListOrders");
        if (orderList.children().length === 0) {
            orderList.html("No orders");

            parentButton.removeClass("btn-success").addClass("btn-secondary");
            parentButtonBadge.attr("value", "");
        } else {
            let listRemainOrders = $(".card-dinein-order")
                .map(function (_, x) {
                    return $(x).attr("order_id");
                })
                .get()
                .join(" ");
            parentButtonBadge.attr("value", listRemainOrders);
        }

        // Re-indexing all current available items
        window.kdsUtils.reIndexing();

        // Re-count all current orders
        window.kdsUtils.reCountOrders(window.kdsUtils.ORDER_TABLE_DINEIN);
    }
);

// Takeaway finish button
$("#dynamic_content").on(
    "click",
    "button.btn-takeaway.btn-finish",
    function (event) {
        let parentCard = $(this).parent().parent().parent();
        let currentId = parentCard.attr("order_id");

        console.log("ID: ", currentId);

        orderId = currentId;
        

        const url = `/update_inventory/${orderId}`;

        $.ajax({
            url: url,
            type: 'POST',
            contentType: 'application/json',
            success: function (result) {
                console.log("Success inventory updated ", result);
                console.log(result);

                // Send API to remove.
                let request = new window.baseRequest({
                    url: '{{ url_for("order_finish") }}',
                    type: "POST",
                    dataType: "json",
                    contentType: "application/json",
                    data: JSON.stringify({
                        order_id: currentId,
                    }),
                });
                request.send();

                // Remove finished parentCard
                parentCard.remove();

                // Recount orders
                window.kdsUtils.reCountOrders(window.kdsUtils.ORDER_TABLE_TAKEAWAY);
            },
            error: function (xhr) {
                displayResult(xhr.responseJSON, xhr.status);
            }
                
        });
    }
);


$("#dynamic_content").on(
    "click",
    "button.btn-takeaway.btn-useractions",
    function (event) {
        console.log("ex")
        
        let parentCard = $(this).parent().parent().parent();

        let currentId = parentCard.attr("order_id");
        let form = $("<form>", {
            method: "POST",
            action: '{{ url_for("order_actions") }}',
            target: "_blank",  // Open in a new tab or window
        });

        // Add an input field with the order_id value
        $("<input>").attr({
            type: "hidden",
            name: "order_id",
            value: currentId,
        }).appendTo(form);

        // Append the form to the body and submit it
        form.appendTo("body").submit();
    }
);



// Takeaway cancel button
$("#dynamic_content").on(
    "click",
    "button.btn-takeaway.btn-cancel",
    function (event) {
        let parentCard = $(this).parent().parent().parent();
        console.log("Parent card : ",parentCard);
        let currentId = parentCard.attr("order_id");
        console.log("Current id : ",currentId);
        // Send API to remove.
        let request = new window.baseRequest({
            url: '{{ url_for("order_cancel") }}',
            type: "POST",
            dataType: "json",
            contentType: "application/json",
            data: JSON.stringify({
                order_id: currentId,
            }),
        });
        request.send();

        // Remove finished parentCard
        parentCard.remove();

        // Recount orders
        window.kdsUtils.reCountOrders(window.kdsUtils.ORDER_TABLE_TAKEAWAY);
    }
);

// Finish an item
$("#dynamic_content").on("click", "input.item-check", function (event) {
    let currentItemId = $(this).attr("item_id");

    let request = new window.baseRequest(
        {
            url: '{{ url_for("item_finish") }}',
            type: "POST",
            dataType: "json",
            contentType: "application/json",
            data: JSON.stringify({
                item_id: currentItemId,
            }),
        },
        sendItemFinishRequestSuccessCallbackFn
    );
    request.send();
});

// Cancel an item
$("#dynamic_content").on("click", "button.item-remove", function (event) {
    let currentItemId = $(this).attr("item_id");

    let request = new window.baseRequest(
        {
            url: '{{ url_for("item_cancel") }}',
            type: "POST",
            dataType: "json",
            contentType: "application/json",
            data: JSON.stringify({
                item_id: currentItemId,
            }),
        },
        sendItemCancelRequestSuccessCallbackFn
    );
    request.send();
});

/**
 * Callback for a success table orders request.
 * @param {Object} response
 * @param {Object} textStatus
 * @param {Object} jqXHR
 */
const getOrdersOfATableSuccessCallbackFn = (response, textStatus, jqXHR) => {
    let orderList = response["order_list"];

    

    // Clear the modal list orders again.
    $("#tableModelListOrders").html("");

    if (orderList.length === 0) {
        $("#tableModelListOrders").html("No orders");
    } else {
        let realOrderList = orderList[0];

        for (let i = 0; i < realOrderList.length; ++i) {
            let currentTemplateInstance = new window.orderTemplate(
                
                realOrderList[i]
             
            );
            
            
            $("#tableModelListOrders").append(
                currentTemplateInstance.getDineInHTML()
            );
        }
    }
};


/**
 * Callback function for a successful item finish request.
 * @param {Object} response
 * @param {Object} textStatus
 * @param {Object} jqXHR
 */
const sendItemFinishRequestSuccessCallbackFn = (
    response,
    textStatus,
    jqXHR
) => {
    let itemId = response["item_id"];
    let currentItemCheckbox = $("#checkbox_item_" + itemId);
    let currentItemLabel = $("#checkbox_item_label_" + itemId);
    let currentItemQuantity = $("#item_quantity_" + itemId);

    if (response["item_status"] == window.kdsUtils.ORDER_ITEM_FINISHED_STATUS) {
        // Add strikes and success class
        currentItemLabel
            .removeClass("strike text-danger")
            .addClass("strike text-success");
        currentItemQuantity
            .removeClass("strike text-danger")
            .addClass("strike text-success");

        // Force the tick to be on
        currentItemCheckbox.prop("checked", true);
    } else {
        // Remove strikes, since the order is now ongoing
        currentItemLabel.removeClass("strike text-success");
        currentItemQuantity.removeClass("strike text-success");

        // Force the tick to be off
        currentItemCheckbox.prop("checked", false);
    }
};

/**
 * Callback for a successful item cancel request.
 * @param {Object} response
 * @param {Object} textStatus
 * @param {Object} jqXHR
 */
const sendItemCancelRequestSuccessCallbackFn = (
    response,
    textStatus,
    jqXHR
) => {
    let itemId = response["item_id"];
    let currentItemCheckbox = $("#checkbox_item_" + itemId);
    let currentItemLabel = $("#checkbox_item_label_" + itemId);
    let currentItemQuantity = $("#item_quantity_" + itemId);

    if (response["item_status"] == window.kdsUtils.ORDER_ITEM_CANCELED_STATUS) {
        // Add strikes and danger class
        currentItemLabel
            .removeClass("strike text-success")
            .addClass("strike text-danger");
        currentItemQuantity
            .removeClass("strike text-success")
            .addClass("strike text-danger");
    } else {
        // Remove strikes and class, since the order is now ongoing
        currentItemLabel.removeClass("strike text-danger");
        currentItemQuantity.removeClass("strike text-danger");
    }

    // In both case, the tick should be off.
    currentItemCheckbox.prop("checked", false);
};

// Function to fetch and display items below threshold in the sidebar
function fetchItemsBelowThreshold() {
    fetch('/check_threshold')  // Fetch data from Flask endpoint
        .then(response => response.json())
        .then(data => {
            // Clear previous content
            document.getElementById('sidebarItemsBelowThreshold').innerHTML = '';

            // Append fetched data to sidebar
            data.forEach(item => {
                let itemElement = document.createElement('li');
                itemElement.className = 'sidebar-item'; // Apply custom class for styling
                itemElement.innerHTML = `&bull; ${item.item_name} - Quantity: ${item.quantity}`;
                document.getElementById('sidebarItemsBelowThreshold').appendChild(itemElement);
            });
        })
        .catch(error => {
            console.error('Error fetching items below threshold:', error);
        });
}

// Call fetchItemsBelowThreshold() when document is ready
document.addEventListener('DOMContentLoaded', function() {
    fetchItemsBelowThreshold();
});