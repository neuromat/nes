

function showDialogAndEnableRemoveButton () {
    // "When there is only one single-line text input field in a form, the user agent should accept Enter in that
    // field as a request to submit the form."
    // http://www.w3.org/MarkUp/html-spec/html-spec_8.html#SEC8.2
    // That's why we need to keep the Exclude button disabled.
    $('#remove_button').prop('disabled', false);

    $('#modalRemove').modal('show');
}

function disableRemoveButton() {
    $('#remove_button').prop('disabled', true);
}
