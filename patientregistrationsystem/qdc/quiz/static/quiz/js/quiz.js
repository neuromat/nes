function showSuccessMessage(message) {
    toastr.options.closeButton = true;
    toastr.options.timeOut = 10000;
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

function showErrorMessageTemporary(message) {
    toastr.options.closeButton = true;
    toastr.options.timeOut = 10000;
    toastr.error(message);
}

function showInfoMessage(message) {
    toastr.options.closeButton = true;
    toastr.options.timeOut = 0;
    toastr.info(message);
}

function jumpToElement(h) {
    var top = document.getElementById(h).offsetTop;
    window.scrollTo(0, top);
}

/**
 * Use if you want to blink some html element.
 * Give it the class blink.
 */
function blink() {
    const updated = $('.blink');
    updated.fadeOut(500);
    updated.fadeIn(500);
}
setInterval(blink, 1000);
