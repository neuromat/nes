/**
 * Created by carlosribas on 14/05/2018.
 */
"use strict";

$(function () {
    $("user_form").on("submit", function (event) {
        if (checkPassExt())
            event.preventDefault();
        if (passwordForce() < 20 && $('#id_new_password1').val()) {
            showErrorMessageTemporary(gettext("Password must contain at least 8 characters, including at least one uppercase letter, digit or special character."));
            event.preventDefault();
        }
    })
});

function Validate() {
    if (!validateForm()) {
        showErrorMessage(gettext('You have to choose at least one user profile!'));
        return false;
    }
    return true;
}

function validateForm() {
    if ($('#optradio_1').is(':checked')) {
        var c = document.getElementsByName('groups');
        for (var i = 0; i < c.length; i++) {
            if (c[i].type == 'checkbox') {
                if (c[i].checked) {
                    return true;
                }
            }
        }
        return false;
    } else {
        return true;
    }
}

$(function () {
    $("user_form").on("submit", function (event) {

        if (checkPassExt()) {
            event.preventDefault();
        }
        if (!$('#email').val()) {
            showErrorMessage(gettext("E-mail have to be filled!"));
            $('#mailDivId').addClass('has-error');
            event.preventDefault();
        }
    })
});

function cancelDisableUser() {
    $("#optradio_0").prop("checked", false);
    $("#optradio_1").prop("checked", true);
    $("#id_username").prop('disabled', false);
    $("#id_new_password1").prop('disabled', true);
    $("#id_new_password2").prop('disabled', true);
    $("#user_account").show();
    $("#profiles").show();
}

function showDialogAndEnableRemoveButton() {
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
