
function showSuccessMessage(message) {
    toastr.options.closeButton = true;
    toastr.options.timeOut = 5000;
    toastr.success(message);
}

function showWarningMessage(message) {
    toastr.options.closeButton = true;
    toastr.options.timeOut = 0;
    toastr.warning(message);
}

function showErrorMessage(message) {
    toastr.options.closeButton = true;
    toastr.options.timeOut = 0;
    toastr.error(message);
}
