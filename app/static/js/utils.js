/**
 * Utility class
 */
export default class KDSUtils {
    /**
     * Global parameters.
     */
    static MAX_BEST_SELLER_ITEMS = 10;
    static CURRENCY = "RM";
    static CURRENCY_DIGIT_PRECISION = 2;
    static AIAOS_FEE = 0.01;

    /**
     * Constants used in the KDS frontend.
     */
    static ORDER_INPROGRESS_STATUS = "0";
    static ORDER_FINISHED_STATUS = "1";
    static ORDER_CANCELED_STATUS = "2";
    static ORDER_REFUNDED_STATUS = "3";
    static ORDER_ITEM_FINISHED_STATUS = "1";
    static ORDER_ITEM_CANCELED_STATUS = "2";
    static ORDER_TABLE_DINEIN = "dine_in";
    static ORDER_TABLE_TAKEAWAY = "take_away";

    /**
     * Reindexing orders in a table.
     */
    static reIndexing = () => {
        // Get current order ID from the screen.
        let currentIndex = $(".btn-table-badge")
            .toArray()
            .map((e) => {
                let currentTableRealOrders = $(e).attr("value");
                if (currentTableRealOrders !== "") {
                    return currentTableRealOrders
                        .trim()
                        .split(" ")
                        .map(Number)
                        .filter(Number);
                }
            })
            .filter(Boolean);

        // Sort them, then map them to the range [1..len(total_orders)]
        let currentIndexFlattern = currentIndex.flat().sort();

        let newIndexMap = {};
        currentIndexFlattern.map((value, index) => {
            newIndexMap[value] = index + 1;
        });

        // Store the index map to localStorage for further usage.
        localStorage.setItem("dinein-orders", currentIndexFlattern.length);

        // Update table button badge (to the correct index).
        $(".btn-table-badge").each((_, e) => {
            let currentList = $(e)
                .attr("value")
                .trim()
                .split(" ")
                .map(Number)
                .filter(Number);
            let newList = currentList.map((value) => {
                return newIndexMap[value];
            });

            $(e).text(newList.join(" - "));
        });
    };

    /**
     * Recound orders to the tab notification.
     * @param {str} tableStatus Status of the current table
     */
    static reCountOrders = (tableStatus) => {
        let currentOrders;

        // Load current orders from localStorage and update to the badge.
        if (tableStatus == this.ORDER_TABLE_DINEIN) {
            currentOrders = localStorage.getItem("dinein-orders");

            if (!currentOrders) {
                currentOrders = 0;
            }

            if (currentOrders == 0) {
                $("#nav-dinein-tab-notification").html("");
            } else {
                $("#nav-dinein-tab-notification").html(currentOrders);
            }
        }

        // Same with take away
        if (tableStatus == this.ORDER_TABLE_TAKEAWAY) {
            currentOrders = $(".card-order-history-collapse").length;

            if (!currentOrders) {
                currentOrders = 0;
            }

            if (currentOrders == 0) {
                $("#nav-takeaway-tab-notification").html("");
            } else {
                $("#nav-takeaway-tab-notification").html(currentOrders);
            }
        }
    };

    /**
     * Parse a week-year input to weekdays
     * @param {String} inp
     * @returns array - weekdays in a week
     */
    static parseDates = (inp) => {
        let year = parseInt(inp.slice(0, 4), 10);
        let week = parseInt(inp.slice(6), 10);

        let day = 1 + (week - 1) * 7; // 1st of January + 7 days for each week

        let dayOffset = new Date(year, 0, 1).getDay(); // we need to know at what day of the week the year start

        dayOffset--; // depending on what day you want the week to start increment or decrement this value. This should make the week start on a monday

        let days = [];
        for (
            let i = 0;
            i < 7;
            i++ // do this 7 times, once for every day
        )
            days.push(new Date(year, 0, day - dayOffset + i)); // add a new Date object to the array with an offset of i days relative to the first day of the week
        return days;
    };

    /**
     * Get week number from a given date
     * @param {Date} d
     * @returns Week number of d
     */
    static getWeekNumber = (d) => {
        // Copy date so don't modify original
        d = new Date(Date.UTC(d.getFullYear(), d.getMonth(), d.getDate()));
        // Set to nearest Thursday: current date + 4 - current day number
        // Make Sunday's day number 7
        d.setUTCDate(d.getUTCDate() + 4 - (d.getUTCDay() || 7));
        // Get first day of year
        var yearStart = new Date(Date.UTC(d.getUTCFullYear(), 0, 1));
        // Calculate full weeks to nearest Thursday
        var weekNo = Math.ceil(((d - yearStart) / 86400000 + 1) / 7);
        // Return array of year and week number
        return [d.getUTCFullYear(), weekNo];
    };

    /**
     * Get weekday from date.
     * @param {String} dateString in DD/MM/YYYY format
     * @returns {Number} a weekday indice
     */
    static getWeekdayIndice = (dateString) => {
        let p = dateString.split("/");
        let d = new Date(+p[2], p[1] - 1, +p[0]);
        return d.getDay();
    };

    /**
     * Get weekday text from indice.
     * @param {Number} indice
     * @returns {String} a weekday text
     */
    static getWeekdayText = (indice) => {
        let weekday = [
            "Sunday",
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
        ];
        return weekday[indice];
    };

    /**
     * Generate one random color
     * @returns {String} a random hex color
     */
    static randomColor = () => {
        let r = Math.floor(Math.random() * 255);
        let g = Math.floor(Math.random() * 255);
        let b = Math.floor(Math.random() * 255);
        return "rgba(" + r + "," + g + "," + b + ", 0.5)";
    };

    /**
     * Generate an array of random rgba colors
     * @param {Number} maxSize
     */
    static poolColors = (maxSize) => {
        let colors = [];
        for (let i = 0; i < maxSize; ++i) {
            colors.push(this.randomColor());
        }
        return colors;
    };
}
