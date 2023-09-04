/**
 * Created by carlosribas on 09/05/2018.
 */

$(document).ready(function () {
    var username_field = $("#id_username");
    var password_flag = $("#password_flag");
    var password1_field = $("#id_new_password1");
    var password2_field = $("#id_new_password2");
    var div_user_account = $("#user_account");
    var div_password = $("#div_password");
    var div_password_flag = $("#div_password_flag");
    var div_profiles = $("#profiles");
    var operation = $("#operation");

    username_field.prop('disabled', true);
    password1_field.prop('disabled', true);
    password2_field.prop('disabled', true);
    div_user_account.hide();
    div_profiles.hide();

    $('input[name = "login_enabled"]').on('change', function(e) {
        if(e.currentTarget.value == "False") {
            console.log("teste")
            username_field.prop('disabled', true);
            username_field.prop('required', false);
            password1_field.prop('disabled', true);
            password1_field.prop('required', false);
            password2_field.prop('disabled', true);
            password2_field.prop('required', false);
            div_user_account.hide();
            div_profiles.hide();
        } else if (e.currentTarget.value == "True") {
            username_field.prop('disabled', false);
            username_field.prop('required', true);
            password1_field.prop('disabled', false);
            password1_field.prop('required', true);
            password2_field.prop('disabled', false);
            password2_field.prop('required', true);
            div_user_account.show();
            div_profiles.show();
        }
    });

    if (optradio_0.checked){
        username_field.prop('disabled', true);
        username_field.prop('required', false);
        password1_field.prop('disabled', true);
        password1_field.prop('required', false);
        password2_field.prop('disabled', true);
        password2_field.prop('required', false);
        div_user_account.hide();
        div_profiles.hide();
    }

    if (optradio_1.checked){
        username_field.prop('disabled', false);
        username_field.prop('required', true);
        password1_field.prop('disabled', false);
        password1_field.prop('required', true);
        password2_field.prop('disabled', false);
        password2_field.prop('required', true);
        div_user_account.show();
        div_profiles.show();
    }

    if(operation.val()=="viewing") {
        username_field.prop('disabled', true);
        password_flag.prop('disabled', true);
        div_password_flag.hide();
        password1_field.prop('disabled', true);
        password2_field.prop('disabled', true);
    }

    if(operation.val()=="editing") {
        if (optradio_1.checked){
            div_password_flag.hide();
            password_flag.prop('checked', false);
            password1_field.prop('disabled', true);
            password1_field.prop('required', false);
            password2_field.prop('disabled', true);
            password2_field.prop('required', false);
        }

        $('input[name = "login_enabled"]').on('change', function(e) {
            if (e.currentTarget.value == "True") {
                username_field.prop('disabled', false);
                username_field.val("");
                password1_field.prop('disabled', false);
                password2_field.prop('disabled', false);
                div_user_account.show();
                div_password.show();
                password_flag.prop('checked', true);
                password_flag.prop('disabled', true);
                div_profiles.show();
            }
        });
    }
});

