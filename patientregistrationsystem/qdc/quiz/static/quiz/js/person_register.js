function checkGroups(element, index, array) {
    // console.log("a[" + index + "] = " + element);
    $('input[name = "groups"]').each(function () {
        if(this.value == element){
            this.checked = true;
        }
    })
}

$(document).ready(function () {
    var username_field = $("#id_username");
    var user_field = $("#id_user");
    var first_name_field = $("#id_first_name");
    var last_name_field = $("#id_last_name");
    var email_field = $("#id_email");
    var password_flag_field = $("#password_flag");
    var user_name_div = $("#user_name_div");
    var user_name_field = $("#id_username");
    var operation = $("#operation");
    $("#id_new_password1").prop('disabled', true);
    $("#id_new_password2").prop('disabled', true);
    $("#text_profiles").collapse({'toggle': false});
    $("#profiles").collapse({'toggle': false});

    if(operation.val()=="viewing") {
        if( typeof user_name_field.val() == 'undefined' || user_name_field.val() == null || user_name_field.val() == ''){
            user_name_div.collapse({'toggle': false});
            user_name_div.collapse('hide');
            $("#profiles").collapse('hide');
        }
        else {
            $("#profiles").collapse('show');
            user_name_div.collapse('show');
        }
        $("#text_profiles").collapse('hide');
        $("#optradio3").prop('checked', true);
        user_field.prop('disabled', false);
        $("#update_password").collapse({'toggle': false});
        $("#password_flag").collapse({'toggle': false});
        $("#update_password").collapse('hide');
        $("#password_flag").collapse('hide');
    }
    if(operation.val()=="editing") {
        $("#div_add_login").prop('disabled', false);
        $("#div_add_login").css('visibility', 'show');
        $("#div_cancel_add_login").prop('disabled', true);
        $("#div_cancel_add_login").css('visibility', 'hidden');
        if(id_username.value != '') {
            $("#profiles").collapse('show');
            $("#optradio3").prop('checked', true);
            $("#text_profiles").collapse('show');
            user_field.prop('disabled', false);
            $("#update_password").collapse('show');
            $("#password_flag").collapse('show');
            user_name_div.collapse({'toggle': true});
            user_name_div.collapse('show');
            id_username.disabled = false;
        } else {
            $("#optradio1").prop('checked', true);
        }
    }

    user_field.change(function () {
        var user_id = user_field.val();
        if(user_id) {
            var url = "/team/person/get_user_attributes/" + user_id;
            $.getJSON(url, function (user) {
                first_name_field.prop('value', user['first_name']);
                last_name_field.prop('value', user['last_name']);
                email_field.prop('value', user['email']);
                $('input[name = "groups"]').prop('checked', false);
                user['groups'].forEach(checkGroups)
            })
        } else {
            first_name_field.prop('value', '');
            last_name_field.prop('value', '');
            email_field.prop('value', '');
        }
    });


    $('input[name = "editPerson"]').on('change', function(e) {
        var person_name = username_field;
    });


    $('input[name = "optradio"]').on('change', function(e) {
        var update_password_div = $("#update_password");
        var password_div = $("#div_password");
        var id_new_password2_form_group_div = $("#id_new_password2_form_group");
        var profiles_div = $("#profiles");
        var operation = $("#operation");
        var password1_field = $("#id_new_password1");
        var password2_field = $("#id_new_password2");
        if(e.currentTarget.value == "1") {
            username_field.prop('disabled', true);
            user_field.prop('disabled', true);
            update_password_div.css('visibility', 'hidden');
            password_div.css('visibility', 'hidden');
            id_new_password2_form_group_div.css('visibility', 'hidden');
            profiles_div.css('visibility', 'hidden');
            if(update_password_div.hasClass('in')) {update_password_div.collapse('hide');}
            if(password_div.hasClass('in')) { password_div.collapse('hide');}
            if(id_new_password2_form_group_div.hasClass('in')) { id_new_password2_form_group_div.collapse('hide');}
            if(profiles_div.hasClass('in')) { profiles_div.collapse('hide');}
        } else if (e.currentTarget.value == "2") {
            username_field.prop('disabled', false);
            user_field.prop('disabled', true);
            if(operation.val()=="editing") {
                update_password_div.css('visibility', 'visible');
                password_div.css('visibility', 'visible');
                id_new_password2_form_group_div.css('visibility', 'visible');
                profiles_div.css('visibility', 'visible');
                update_password_div.collapse('visible');
                password_div.collapse('show');
                id_new_password2_form_group_div.collapse('show');
                profiles_div.collapse('show');
                password1_field.prop('disabled', false);
                password2_field.prop('disabled', false);
                $("#div_add_login").prop('disabled', false);
                $("#div_add_login").css('visibility', 'show');
                $("#div_cancel_add_login").prop('disabled', true);
                $("#div_cancel_add_login").css('visibility', 'hidden');
            }
            else {
                update_password_div.css('visibility', 'hidden');
                password_div.css('visibility', 'visible');
                id_new_password2_form_group_div.css('visibility', 'visible');
                profiles_div.css('visibility', 'visible');
                update_password_div.collapse('hide');
                password_div.collapse('show');
                id_new_password2_form_group_div.collapse('show');
                profiles_div.collapse('show');
                password1_field.prop('disabled', false);
                password2_field.prop('disabled', false);
                $("#div_add_login").prop('disabled', true);
                $("#div_add_login").css('visibility', 'hidden');
                $("#div_cancel_add_login").prop('disabled', false);
                $("#div_cancel_add_login").css('visibility', 'show');
            }
        } else if (e.currentTarget.value == "3") {
            username_field.prop('disabled', true);
            user_field.prop('disabled', false);
            update_password_div.css('visibility', 'visible');
            password_div.css('visibility', 'visible');
            id_new_password2_form_group_div.css('visibility', 'visible');
            profiles_div.css('visibility', 'visible');
            update_password_div.collapse('show');
            password_div.collapse('show');
            id_new_password2_form_group_div.collapse('show');
            profiles_div.collapse('show');

            if(operation.val()=="editing") {
                password1_field.prop('disabled', false);
                password2_field.prop('disabled', false);
                update_password_div.collapse('hide');
            }
        }
    });

    password_flag_field.change(function () {
        var password_div = $("#div_password");
        var id_new_password2_form_group_div = $("#id_new_password2_form_group");
        var password_field = $("#id_new_password1");
        var password2_field = $("#id_new_password2");
        if($("#password_flag").is(":checked")){
            password_field.prop('disabled', false);
            password2_field.prop('disabled', false);
            password_div.collapse('show');
            id_new_password2_form_group_div.collapse('show');
        } else {
            password_field.prop('disabled', true);
            password2_field.prop('disabled', true);
            password_div.collapse('hide');
            id_new_password2_form_group_div.collapse('hide');
        }
    });
});

function showDialogAndEnableRemoveButton () {
    $('#remove_button').prop('disabled', false);
    $('#modalRemove').modal('show');
}

function disableRemoveButton() {
    $('#remove_button').prop('disabled', true);
}

function deactivate_user (id) {
    disableDeactivateButton();
}

function showDialogAndEnableDeactiveteUserButton (id) {
    $('#deactivate_button').prop('disabled', false);
    $('#modalDeactivate').modal('show');
}

function disableDeactivateButton() {
    $('#modalDeactivate').prop('disabled', true);
}

function add_user (id) {
    $("#user_name_div").collapse({'toggle': false});
    $("#text_profiles").collapse({'toggle': false});
    $("#profiles").collapse({'toggle': false});
    $("#update_password").collapse({'toggle': false});
    $("#div_password").collapse({'toggle': false});
    $("#id_new_password2_form_group").collapse({'toggle': false});
    $("#password_flag").collapse({'toggle': false});
    $("#div_add_login").collapse({'toggle': false});
    $("#user_name_div").collapse('show');
    $("#text_profiles").collapse('show');
    $("#profiles").collapse('show');
    $("#update_password").collapse('hide');
    $("#div_password").collapse('show');
    $("#id_new_password2_form_group").collapse('show');
    $("#password_flag").collapse('hide');
    $("#div_add_login").prop('disabled', true);
    $("#div_add_login").css('visibility', 'hidden');
    $("#div_cancel_add_login").prop('disabled', false);
    $("#div_cancel_add_login").css('visibility', 'visible');
    $("#id_username").prop('disabled', false);
    $("#id_new_password1").prop('disabled', false);
    $("#id_new_password2").prop('disabled', false);
}

function cancel_add_user (id) {
    $("#user_name_div").collapse({'toggle': false});
    $("#text_profiles").collapse({'toggle': false});
    $("#profiles").collapse({'toggle': false});
    $("#update_password").collapse({'toggle': false});
    $("#div_password").collapse({'toggle': false});
    $("#id_new_password2_form_group").collapse({'toggle': false});
    $("#password_flag").collapse({'toggle': false});
    $("#div_add_login").collapse({'toggle': false});
    $("#user_name_div").collapse('hide');
    $("#text_profiles").collapse('hide');
    $("#profiles").collapse('hide');
    $("#update_password").collapse('hide');
    $("#div_password").collapse('hide');
    $("#id_new_password2_form_group").collapse('hide');
    $("#password_flag").collapse('hide');
    $("#div_add_login").prop('disabled', false);
    $("#div_add_login").css('visibility', 'visible');
    $("#div_cancel_add_login").prop('disabled', true);
    $("#div_cancel_add_login").css('visibility', 'hidden');
    $("#id_username").prop('disabled', true);
    $("#id_new_password1").prop('disabled', true);
    $("#id_new_password2").prop('disabled', true);
}
