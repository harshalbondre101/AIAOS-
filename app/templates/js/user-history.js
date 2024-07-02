$(document).ready(() => {
    $("#user-history-table").dataTable({
        ajax: {
            url: "{{ url_for('user_get') }}",
            dataSrc: "user_list",
        },
        columns: [
            {
                data: "user_name",
                defaultContent: "(Not set)",
            },
            { data: "user_phone" },
            { data: "user_points" },
            { data: "user_spent" },
            { data: "user_orders" },
        ],
        order: [
            [2, "DESC"],
            [3, "DESC"],
            [4, "DESC"],
        ],
        columnDefs: [
            {
                // Points should be in 2 digits float.
                render: (data, type, row) =>
                    data.toFixed(window.kdsUtils.CURRENCY_DIGIT_PRECISION),
                targets: [3],
            },
        ],
    });
});
