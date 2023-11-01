"use strict";

function showSuccessMessage(message) {
    bootstrap.showToast({
        header: "",
        headerSmall: "",
        body: message,
        closeButton: true,
        closeButtonLabel: "close",
        closeButtonClass: "",
        toastClass: "bg-success",
        animation: true,
        delay: 0,
        position: "top-0 end-0",
        direction: "append",
        ariaLive: "assertive",
    })
}

function showWarningMessage(message) {
    bootstrap.showToast({
        header: "",
        headerSmall: "",
        body: message,
        closeButton: true,
        closeButtonLabel: "close",
        closeButtonClass: "",
        toastClass: "bg-success",
        animation: true,
        delay: 10000,
        position: "top-0 end-0",
        direction: "append",
        ariaLive: "assertive",
    })
}

function showErrorMessage(message) {
    bootstrap.showToast({
        header: "",
        headerSmall: "",
        body: message,
        closeButton: true,
        closeButtonLabel: "close",
        closeButtonClass: "",
        toastClass: "bg-danger",
        animation: true,
        delay: 0,
        position: "top-0 end-0",
        direction: "append",
        ariaLive: "assertive",
    })
}

function showErrorMessageTemporary(message) {
    bootstrap.showToast({
        header: "",
        headerSmall: "",
        body: message,
        closeButton: true,
        closeButtonLabel: "close",
        closeButtonClass: "",
        toastClass: "bg-danger",
        animation: true,
        delay: 10000,
        position: "top-0 end-0",
        direction: "append",
        ariaLive: "assertive",
    })
}

function showInfoMessage(message) {
    bootstrap.showToast({
        header: "",
        headerSmall: "",
        body: message,
        closeButton: true,
        closeButtonLabel: "close",
        closeButtonClass: "",
        toastClass: "bg-info",
        animation: true,
        delay: 0,
        position: "top-0 end-0",
        direction: "append",
        ariaLive: "assertive",
    })
}

function jumpToElement(h) {
    const top = document.getElementById(h).offsetTop;
    window.scrollTo(0, top);
}

async function fetch_post(url, data, success) {
    const data_form = new FormData();

    for (var key in data) {
        if (data.hasOwnProperty(key)) {
            data_form.append(key, data[key]);
        }
    }

    try {
        const response = await fetch(url, {
            method: "POST",
            body: data_form,
            credentials: 'same-origin',
        });
        const result = await response.text();
        console.log(result);
        success(result);
    } catch (error) {
        console.error("Error:", error);
    }
}

function ready(fn) {
    if (document.readyState !== 'loading') {
        fn();
    } else {
        document.addEventListener('DOMContentLoaded', fn);
    }
}