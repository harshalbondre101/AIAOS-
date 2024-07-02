// PIN login input
var pinLogin = $("#pinInput").pinlogin({
    fields: 6,
    hideinput: false,
    reset: false,
});

// Modal instance
var pinModalInstance = new bootstrap.Modal($("#pinModal"));
