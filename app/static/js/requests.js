/**
 * Base HTTP AJAX request for the application.
 */
export default class BaseRequest {
    /**
     * Constructor for the BaseRequest
     * @param {Object} ajaxObject
     * @param {Function} successCallbackFn
     * @param {Function} failedCallbackFn
     */
    constructor(ajaxObject, successCallbackFn, failedCallbackFn) {
        this._ajaxObject = ajaxObject;

        // Default success callback function
        if (successCallbackFn) {
            this._successCallbackFn = successCallbackFn;
        } else {
            this._successCallbackFn = (response, textStatus, jqXHR) => {
                console.log(response, textStatus);
            };
        }

        // Default failed callback function
        if (failedCallbackFn) {
            this._failedCallbackFn = failedCallbackFn;
        } else {
            this._failedCallbackFn = (jqXHR, textStatus, errorThrown) => {
                console.log(textStatus, errorThrown);
            };
        }
    }

    /**
     * Set the url for a request
     * @param {String} url
     */
    set setUrl(url) {
        this._ajaxObject["url"] = url;
    }

    /**
     * Set the data for a request
     * @param {Object} data
     */
    set setData(data) {
        this._ajaxObject["data"] = data;
    }

    /**
     * Set the method for a request
     * @param {String} method
     */
    set setMethod(method) {
        this._ajaxObject["method"] = method;
    }

    /**
     * Send a request and use callback functions based on the response.
     */
    send() {
        let request = $.ajax(this._ajaxObject);
        request.done(this._successCallbackFn);
        request.fail(this._failedCallbackFn);
    }
}
