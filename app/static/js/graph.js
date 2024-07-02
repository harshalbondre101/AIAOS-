/**
 * Display graphing
 *
 */
export default class Graph {
    /**
     * Constructor for the Graph
     * @param {Object} orderList list of orders in that week
     */
    constructor(orderList) {
        this._orderList = orderList;
        this._totalOrders = orderList.length;
    }

    /**
     * Get the orders summarize (finished, canceled and refunded) from the orderList
     * @returns {Array} data to fit to Chart.js
     */
    _orderSummarize = () => {
        // Count list of order types.
        let _totalInProgressOrders = this._orderList.filter(
            (x) => x.order_status == window.kdsUtils.ORDER_INPROGRESS_STATUS
        ).length;

        let _totalFinishedOrders = this._orderList.filter(
            (x) => x.order_status == window.kdsUtils.ORDER_FINISHED_STATUS
        ).length;

        let _totalCanceledOrders = this._orderList.filter(
            (x) => x.order_status == window.kdsUtils.ORDER_CANCELED_STATUS
        ).length;

        let _totalRefundedOrders = this._orderList.filter(
            (x) => x.order_status == window.kdsUtils.ORDER_REFUNDED_STATUS
        ).length;

        // Data for the pie chart showing number of finished, canceled and refunded orders
        let _pieChartData = [
            { name: "Finished", count: _totalFinishedOrders },
            { name: "Canceled", count: _totalCanceledOrders },
            { name: "Refunded", count: _totalRefundedOrders },
        ];

        return _pieChartData;
    };

    /**
     * Get the sales per day.
     * @returns {Array} data to fit to Chart.js
     */
    _salesPerDay = () => {
        let _ordersAndDates = this._orderList
            .filter(
                (x) => x.order_status == window.kdsUtils.ORDER_FINISHED_STATUS
            )
            .map((y) => ({
                finish_date: y.order_finish_date.split(" ")[0],
                order_items: y.order_items,
            }));

        let dates = _ordersAndDates.map((x) => x.finish_date);
        let uniqueDates = [...new Set(dates)];

        // Create the object of {day, sales}
        let itemSalePerDay = uniqueDates.map((y) => ({
            finish_date_indice: window.kdsUtils.getWeekdayIndice(y),
            sales: _ordersAndDates
                .filter((z) => z.finish_date == y)
                .map((t) => t.order_items)
                .flat()
                .filter(
                    (u) =>
                        u.item_status ==
                        window.kdsUtils.ORDER_ITEM_FINISHED_STATUS
                )
                .map((v) => v.item_quantity * v.item_price)
                .reduce((w, x) => w + x, 0),
        }));

        for (let i = 0; i < 7; ++i) {
            if (
                itemSalePerDay.filter((x) => x.finish_date_indice == i)
                    .length == 0
            ) {
                itemSalePerDay.push({
                    finish_date_indice: i,
                    sales: 0,
                });
            }
        }

        // Sort for displaying
        itemSalePerDay.sort(
            (a, b) => a.finish_date_indice - b.finish_date_indice
        );

        return itemSalePerDay;
    };

    /**
     * Get maxBestItems items from the orderList
     * @param {Number} maxBestItems
     * @returns {Array} list of maxBestItems items to fit to Chart.js
     */
    _bestItemSeller = (maxBestItems) => {
        // Data for the bar chart showing best items
        let finishedItemData = this._orderList
            .filter(
                (w) => w.order_status == window.kdsUtils.ORDER_FINISHED_STATUS
            )
            .map((x) => x.order_items)
            .flat();

        let itemNames = finishedItemData.map((x) => x.item_name);
        let uniqueItemNames = [...new Set(itemNames)];

        // Create the object of {item_name, item_quantity}
        // sort descending and return elements in [0, maxBestItems]
        let bestItemSeller = uniqueItemNames
            .map((y) => ({
                item_name: y,
                item_quantity: finishedItemData
                    .filter((z) => z.item_name === y)
                    .map((t) => t.item_quantity)
                    .reduce((u, v) => u + v, 0),
            }))
            .sort((a, b) => b.item_quantity - a.item_quantity)
            .slice(0, maxBestItems);

        return bestItemSeller;
    };

    /**
     * Get Pie chart - summarize the orders (finished, failed and refunded).
     * @returns {String} HTML render of the chart.
     */
    getPieSummarizeHTML = () => {
        let pieChartData = this._orderSummarize();

        let wrapper = $(document.createElement("div"));
        wrapper.addClass("col-xs-4 col-md-4 col-sm-4 col-lg-4");

        let pieChartDiv = $(document.createElement("canvas"));
        pieChartDiv.attr("id", "pieSummarizeChart");

        // Chart.js pie chart
        let pieSummarizeChart = new Chart(pieChartDiv, {
            type: "pie",
            data: {
                labels: pieChartData.map((row) => row.name),
                datasets: [
                    {
                        data: pieChartData.map((row) => row.count),
                        backgroundColor: [
                            "rgb(75, 192, 192)",
                            "rgb(255, 99, 132)",
                            "rgb(255, 205, 86)",
                        ],
                    },
                ],
            },
            options: {
                plugins: {
                    title: {
                        display: true,
                        text: "Sales summarize",
                    },
                },
            },
        });

        wrapper.append(pieChartDiv);
        return wrapper;
    };

    /**
     * Get sales per weekday.
     * @returns {String} HTML render of the chart.
     */
    getLineItemPerWeekdaysHTML = () => {
        let salesPerDay = this._salesPerDay();

        let wrapper = $(document.createElement("div"));
        wrapper.addClass("row");

        let histChartDiv = $(document.createElement("canvas"));
        histChartDiv.attr("id", "histSalesWeekChart");

        // Chart.js chart
        let histSalesWeekChart = new Chart(histChartDiv, {
            type: "line",
            data: {
                labels: salesPerDay.map((row) =>
                    window.kdsUtils.getWeekdayText(row.finish_date_indice)
                ),
                datasets: [
                    {
                        data: salesPerDay.map((row) => row.sales),
                        datalabels: {
                            align: "end",
                            anchor: "end",
                        },
                    },
                ],
            },
            options: {
                // Core options
                aspectRatio: 5 / 3,
                layout: {
                    padding: {
                        top: 32,
                        right: 16,
                        bottom: 16,
                        left: 8,
                    },
                },
                elements: {
                    line: {
                        fill: false,
                        tension: 0.4,
                    },
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: "Sales (in " + window.kdsUtils.CURRENCY + ")",
                        },
                    },
                    x: {
                        title: {
                            display: true,
                            text: "Weekday",
                        },
                    },
                },
                plugins: {
                    datalabels: {
                        backgroundColor: (context) => {
                            return context.dataset.backgroundColor;
                        },
                        borderRadius: 4,
                        color: "white",
                        font: {
                            weight: "bold",
                        },
                        padding: 6,
                        formatter: (val, context) => {
                            return val.toFixed(
                                window.kdsUtils.CURRENCY_DIGIT_PRECISION
                            );
                        },
                    },
                    title: {
                        display: true,
                        text: "Sales per day",
                    },
                    legend: {
                        display: false,
                    },
                },
            },
        });

        wrapper.append(histChartDiv);

        return wrapper;
    };

    /**
     * Get histogram of best sellers (by sales).
     * @param {Number} maxItems maximum items to display.
     * @returns {String} HTML render of the chart.
     */
    getHistBestSellerHTML = (maxItems) => {
        let bestItemSellerData = this._bestItemSeller(maxItems);

        let wrapper = $(document.createElement("div"));
        wrapper.addClass("col-md-8 col-xs-8 col-lg-8 col-sm-8");

        let histChartDiv = $(document.createElement("canvas"));
        histChartDiv.attr("id", "histBestItemsChart");

        // Chart.js bar chart
        let histBestItemsChart = new Chart(histChartDiv, {
            type: "bar",
            data: {
                labels: bestItemSellerData.map((row) => row.item_name),
                datasets: [
                    {
                        label: "Item quantity",
                        data: bestItemSellerData.map(
                            (row) => row.item_quantity
                        ),
                        datalabels: {
                            anchor: "end",
                            align: "start",
                        },
                        // Random colors for the bar chart.
                        backgroundColor: window.kdsUtils.poolColors(
                            bestItemSellerData.length
                        ),
                    },
                ],
            },
            options: {
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: "Item name",
                        },
                    },
                    x: {
                        title: {
                            display: true,
                            text: "Item quantity",
                        },
                    },
                },
                indexAxis: "y",
                plugins: {
                    datalabels: {
                        color: "grey",
                        font: {
                            weight: "bold",
                        },
                        formatter: Math.round,
                    },
                    title: {
                        display: true,
                        text: "Best " + maxItems + " items by quantity",
                    },
                    legend: {
                        display: false,
                    },
                },
            },
        });

        wrapper.append(histChartDiv);
        return wrapper;
    };
}
