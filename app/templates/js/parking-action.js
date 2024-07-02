// When click the "Submit" button
$("#submitBottleParking").on("click", () => {
    let customerPhone = $("#customerPhone").val();
    let bottleName = $("#bottleName").val();
    let bottleAmounts = $("#bottleAmounts").val();
    let expirationDate = $("#expirationDate").val();

    let request = new window.baseRequest(
        {
            url: "{{ url_for('bottle_parking_submit') }}",
            type: "POST",
            dataType: "json",
            contentType: "application/json",
            data: JSON.stringify({
                customer_phone: customerPhone,
                bottle_name: bottleName,
                bottle_amounts: bottleAmounts,
                expiration_date: expirationDate,
            }),
        },
        parkingBottleSuccessCallbackFn,
        parkingBottleFailedCallbackFn
    );

    request.send();
});

/**
 * Callback function for a successful parking bottle request
 * @param {Object} response
 * @param {Object} textStatus
 * @param {Object} jqXHR
 */
const parkingBottleSuccessCallbackFn = (response, textStatus, jqXHR) => {
    // Do nothing
};

/**
 * Callback function for a failed parking bottle request
 * @param {Object} jqXHR
 * @param {Object} textStatus
 * @param {Object} errorThrown
 */
const parkingBottleFailedCallbackFn = (jqXHR, textStatus, errorThrown) => {
    // Do nothing
};
