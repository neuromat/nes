/**
 * Created by antonioferraoneto on 22/09/16.
 */

$(document).ready(function () {
    var user_field = $("#id_user");
    var first_name_field = $("#id_first_name");
    var last_name_field = $("#id_last_name");
    var email_field = $("#id_email");

    user_field.change(function () {

        var user_id = user_field.val();

        if(user_id) {
            var url = "/team/person/get_user_attributes/" + user_id;

            $.getJSON(url, function (user) {
                first_name_field.prop('value', user['first_name']);
                last_name_field.prop('value', user['last_name']);
                email_field.prop('value', user['email']);
            })
        } else {
            first_name_field.prop('value', '');
            last_name_field.prop('value', '');
            email_field.prop('value', '');
        }

    })

});

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
