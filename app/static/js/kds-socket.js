$(document).ready(() => {
    // Re-indexing all element available to a [1, ..] index.
    window.kdsUtils.reIndexing();

    // Keep active tab in the local storage
    $("a[data-bs-toggle='tab']").on("show.bs.tab", (e) => {
        localStorage.setItem("activeTab", $(e.target).attr("id"));
    });

    // And when refresh, activate it.
    var activeTab = localStorage.getItem("activeTab");

    if (activeTab) {
        $("#" + activeTab).tab("show");
    }

    // Visibility problem: auto refresh when the page is off - on.
    var refresh = false;

    document.addEventListener("visibilitychange", () => {
        if (document.visibilityState === "hidden") {
            refresh = true;
        } else if (document.visibilityState === "visible") {
            if (refresh) {
                window.location.reload();
            }
        }
    });

    // Socket
    var socket = io();

    socket.on("message", (message) => {
        let newOrderType = message.order_type;
        let notification = $("#notification");
        let notificationMessage = $("#notificationMessage");
        let notificationSound = $("#notificationSound")[0];

        if (newOrderType == window.kdsUtils.ORDER_TABLE_DINEIN) {
            let tableNum = message.data.order_table;
            let tableOrders = message.data.table_data[0]
                .map((a) => a.order_id)
                .join(" ");

            // Change table button status
            let tableButton = $("#table_id_" + tableNum);
            tableButton.removeClass("btn-secondary").addClass("btn-success");

            let tableButtonBadge = $("#table_id_" + tableNum + "_badge");
            tableButtonBadge.attr("value", tableOrders);

            // Re-indexing all tables
            window.kdsUtils.reIndexing();

            // If the modal of that table is currently active, add new order to the bottom.
            if (
                $("#tableModal").hasClass("show") &&
                $("#tableModalLabel").text() == tableNum
            ) {
                let newTemplateInstance = new window.orderTemplate(
                    message.data.table_data[0].at(-1)
                );

                if (
                    $("#tableModelListOrders div").hasClass("card-dinein-order")
                ) {
                    $("#tableModelListOrders").append(
                        newTemplateInstance.getDineInHTML()
                    );
                } else {
                    $("#tableModelListOrders").html(
                        newTemplateInstance.getDineInHTML()
                    );
                }
            }

            // Send notification
            notificationMessage.text("Table " + tableNum + " has a new order");
            notification.show();
            notificationSound.play();

            // Update status badge for the tab
            window.kdsUtils.reCountOrders(window.kdsUtils.ORDER_TABLE_DINEIN);
        } else if (newOrderType == window.kdsUtils.ORDER_TABLE_TAKEAWAY) {
            let newTemplateInstance = new window.orderTemplate(
                message.data.order_data
            );
            $("#nav-takeaway").append(newTemplateInstance.getTakeAwayHTML());

            // Send notification
            notificationMessage.text("There is a new takeaway order");
            notification.show();
            notificationSound.play();

            // Update the tab's badge.
            window.kdsUtils.reCountOrders(window.kdsUtils.ORDER_TABLE_TAKEAWAY);
        }
    });
});
