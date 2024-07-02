// Import and set classes as a global variable to use in other files.
import { OrderTemplate, StatsHeaderTemplate } from "./templates.js";
import KDSUtils from "./utils.js";
import BaseRequest from "./requests.js";
import Graph from "./graph.js";

window.orderTemplate = OrderTemplate;
window.statTemplate = StatsHeaderTemplate;
window.graph = Graph;
window.kdsUtils = KDSUtils;
window.baseRequest = BaseRequest;

// Set chart global datatype
Chart.register(ChartDataLabels);

// Closing notification.
$("#notificationClose").on("click", () => {
    $("#notification").hide();
});
