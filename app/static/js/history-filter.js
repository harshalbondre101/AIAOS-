window.addEventListener("DOMContentLoaded", (event) => {
    let current_date = new Date();
    document.getElementById("filterStart").valueAsDate = current_date;
    document.getElementById("filterEnd").valueAsDate = current_date;
});

$("#filterStatus").select2({
    theme: "bootstrap-5",
    width: $(this).data("width")
        ? $(this).data("width")
        : $(this).hasClass("w-100")
        ? "100%"
        : "style",
    placeholder: $(this).data("placeholder"),
    closeOnSelect: false,
});
$("#filterTable").select2({
    theme: "bootstrap-5",
    width: $(this).data("width")
        ? $(this).data("width")
        : $(this).hasClass("w-100")
        ? "100%"
        : "style",
    placeholder: $(this).data("placeholder"),
    closeOnSelect: false,
});
